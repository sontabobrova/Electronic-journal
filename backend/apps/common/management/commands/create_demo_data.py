from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.education.models import (
    AcademicGroup,
    AcademicPeriod,
    StudentProfile,
    Subject,
    TeacherProfile,
    TeachingAssignment,
)
from apps.journal.models import (
    AttendanceRecord,
    AttendanceStatus,
    ClassSession,
    Grade,
    GradeWork,
    GradeWorkType,
)
from apps.notifications.tasks import send_session_closing_reminders
from apps.users.models import User, UserRole


class Command(BaseCommand):
    help = "Create idempotent demo data for acceptance testing."

    def handle(self, *args, **options):
        today = timezone.localdate()

        self._upsert_user(
            username="admin",
            password="admin123",
            role=UserRole.ADMIN,
            first_name="Админ",
            last_name="Системы",
            email="admin@example.local",
            phone="+7 900-000-00-01",
            is_staff=True,
            is_superuser=True,
        )
        teacher = self._upsert_user(
            username="teacher",
            password="teacher123",
            role=UserRole.TEACHER,
            first_name="Ирина",
            last_name="Петрова",
            email="teacher@example.local",
            phone="+7 900-000-00-02",
        )
        student = self._upsert_user(
            username="student",
            password="student123",
            role=UserRole.STUDENT,
            first_name="Алексей",
            last_name="Иванов",
            email="student@example.local",
            phone="+7 900-000-00-03",
        )

        group, _ = AcademicGroup.objects.update_or_create(
            name="743-2",
            defaults={"enrollment_year": today.year - 1, "is_active": True},
        )
        subject, _ = Subject.objects.update_or_create(
            code="IB-101",
            defaults={
                "name": "Информационная безопасность",
                "description": "Демонстрационная дисциплина для приемочного сценария.",
                "is_active": True,
            },
        )
        period, _ = AcademicPeriod.objects.update_or_create(
            name="Демо период",
            defaults={
                "starts_at": today - timedelta(days=30),
                "ends_at": today + timedelta(days=3),
                "is_active": True,
            },
        )

        teacher_profile, _ = TeacherProfile.objects.update_or_create(
            user=teacher,
            defaults={
                "personnel_number": "DEMO-T-001",
                "position": "Преподаватель",
            },
        )
        student_profile, _ = StudentProfile.objects.update_or_create(
            user=student,
            defaults={
                "student_id": 100001,
                "group": group,
                "enrollment_date": today - timedelta(days=365),
            },
        )
        assignment, _ = TeachingAssignment.objects.get_or_create(
            teacher=teacher_profile,
            subject=subject,
            group=group,
            period=period,
        )

        grade_work, _ = GradeWork.objects.update_or_create(
            assignment=assignment,
            title="Практическая работа 1",
            work_date=today,
            defaults={
                "work_type": GradeWorkType.CLASSWORK,
                "max_score": Decimal("5.00"),
                "weight": Decimal("1.00"),
                "created_by": teacher,
            },
        )
        Grade.objects.update_or_create(
            work=grade_work,
            student=student_profile,
            defaults={
                "value": Decimal("5.00"),
                "comment": "Демо-оценка для приемки.",
                "created_by": teacher,
                "updated_by": teacher,
            },
        )

        class_session, _ = ClassSession.objects.update_or_create(
            assignment=assignment,
            session_date=today,
            topic="Вводное занятие по защите информации",
            defaults={"created_by": teacher},
        )
        AttendanceRecord.objects.update_or_create(
            session=class_session,
            student=student_profile,
            defaults={
                "status": AttendanceStatus.PRESENT,
                "comment": "Присутствовал на демо-занятии.",
                "created_by": teacher,
                "updated_by": teacher,
            },
        )

        created_reminders = send_session_closing_reminders()

        self.stdout.write(self.style.SUCCESS("Demo data is ready."))
        self.stdout.write("Credentials:")
        self.stdout.write("  admin / admin123")
        self.stdout.write("  teacher / teacher123")
        self.stdout.write("  student / student123")
        self.stdout.write(f"Created reminders: {created_reminders}")
        self.stdout.write(f"Demo period ends at: {period.ends_at.isoformat()}")

    def _upsert_user(
        self,
        *,
        username: str,
        password: str,
        role: str,
        first_name: str,
        last_name: str,
        email: str,
        phone: str,
        is_staff: bool = False,
        is_superuser: bool = False,
    ) -> User:
        user, _ = User.objects.update_or_create(
            username=username,
            defaults={
                "role": role,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone": phone,
                "is_active": True,
                "is_staff": is_staff,
                "is_superuser": is_superuser,
                "access_expires_at": None,
                "failed_login_attempts": 0,
                "locked_until": None,
            },
        )
        user.set_password(password)
        user.save(update_fields=["password"])
        return user
