import os
import random

from locust import HttpUser, between, task


def parse_credentials(env_name: str, default: str) -> list[tuple[str, str]]:
    raw_value = os.getenv(env_name, default)
    credentials = []
    for item in raw_value.split(","):
        if not item.strip():
            continue
        username, separator, password = item.partition(":")
        if not separator:
            continue
        credentials.append((username.strip(), password.strip()))
    return credentials


ADMIN_CREDENTIALS = parse_credentials("LOADTEST_ADMIN_CREDENTIALS", "admin:admin123")
TEACHER_CREDENTIALS = parse_credentials(
    "LOADTEST_TEACHER_CREDENTIALS",
    "teacher:teacher123,demo_teacher_01:teacher123,demo_teacher_02:teacher123,demo_teacher_03:teacher123,demo_teacher_04:teacher123,demo_teacher_05:teacher123",
)
STUDENT_CREDENTIALS = parse_credentials(
    "LOADTEST_STUDENT_CREDENTIALS",
    "student:student123,demo_student_001:student123,demo_student_002:student123,demo_student_003:student123,demo_student_004:student123,demo_student_005:student123",
)
ENABLE_WRITES = os.getenv("LOADTEST_ENABLE_WRITES", "false").lower() in {"1", "true", "yes", "on"}


class AuthenticatedApiUser(HttpUser):
    abstract = True
    wait_time = between(1, 3)
    credentials: list[tuple[str, str]] = []

    def on_start(self) -> None:
        self.headers = {}
        username, password = random.choice(self.credentials)
        with self.client.post(
            "/api/auth/login/",
            json={"username": username, "password": password},
            name="POST /api/auth/login/",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"login failed: HTTP {response.status_code}")
                return

            token = response.json().get("token")
            if not token:
                response.failure("login response has no token")
                return

            self.headers = {"Authorization": f"Token {token}"}

    def get_api(self, path: str, name: str | None = None) -> None:
        if not self.headers:
            return
        self.client.get(path, headers=self.headers, name=name or f"GET {path}")

    def post_api(self, path: str, payload: dict, name: str | None = None) -> None:
        if not self.headers:
            return
        self.client.post(path, json=payload, headers=self.headers, name=name or f"POST {path}")


class AdminApiUser(AuthenticatedApiUser):
    weight = 1
    credentials = ADMIN_CREDENTIALS

    @task(4)
    def dashboard(self) -> None:
        self.get_api("/api/admin-cabinet/dashboard/", "GET admin dashboard")

    @task(3)
    def users_and_profiles(self) -> None:
        self.get_api("/api/users/", "GET users")
        self.get_api("/api/education/students/", "GET student profiles")
        self.get_api("/api/education/teachers/", "GET teacher profiles")

    @task(3)
    def education_reference_data(self) -> None:
        self.get_api("/api/education/groups/", "GET groups")
        self.get_api("/api/education/subjects/", "GET subjects")
        self.get_api("/api/education/periods/", "GET periods")
        self.get_api("/api/education/teaching-assignments/", "GET assignments")

    @task(1)
    def audit_and_reports(self) -> None:
        self.get_api("/api/audit/logs/", "GET audit logs")
        self.get_api("/api/reports/requests/", "GET report requests")

    @task(1)
    def generate_report_if_enabled(self) -> None:
        if ENABLE_WRITES:
            self.post_api(
                "/api/reports/requests/generate/",
                {"report_type": "grades", "file_format": "csv", "parameters": {}},
                "POST generate grades report",
            )


class TeacherApiUser(AuthenticatedApiUser):
    weight = 3
    credentials = TEACHER_CREDENTIALS

    @task(4)
    def dashboard_and_assignments(self) -> None:
        self.get_api("/api/journal/teacher/dashboard/", "GET teacher dashboard")
        self.get_api("/api/journal/teacher/assignments/", "GET teacher assignments")

    @task(4)
    def journal_data(self) -> None:
        self.get_api("/api/journal/teacher/students/", "GET teacher students")
        self.get_api("/api/journal/teacher/grade-works/", "GET teacher grade works")
        self.get_api("/api/journal/teacher/grades/", "GET teacher grades")

    @task(3)
    def attendance_data(self) -> None:
        self.get_api("/api/journal/teacher/class-sessions/", "GET teacher sessions")
        self.get_api("/api/journal/teacher/attendance/", "GET teacher attendance")

    @task(1)
    def notifications_and_reports(self) -> None:
        self.get_api("/api/notifications/notifications/", "GET notifications")
        self.get_api("/api/reports/requests/", "GET report requests")

    @task(1)
    def generate_report_if_enabled(self) -> None:
        if ENABLE_WRITES:
            self.post_api(
                "/api/reports/requests/generate/",
                {"report_type": "attendance", "file_format": "csv", "parameters": {}},
                "POST generate attendance report",
            )


class StudentApiUser(AuthenticatedApiUser):
    weight = 4
    credentials = STUDENT_CREDENTIALS

    @task(5)
    def dashboard(self) -> None:
        self.get_api("/api/journal/student/dashboard/", "GET student dashboard")

    @task(4)
    def grades(self) -> None:
        self.get_api("/api/journal/student/grades/", "GET student grades")

    @task(4)
    def attendance(self) -> None:
        self.get_api("/api/journal/student/attendance/", "GET student attendance")
