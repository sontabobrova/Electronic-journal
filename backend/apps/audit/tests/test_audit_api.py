from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from apps.audit.models import AuditAction, AuditLog
from apps.education.models import AcademicGroup, AcademicPeriod, StudentProfile, Subject, TeacherProfile, TeachingAssignment
from apps.journal.models import GradeWork
from apps.users.models import UserRole


pytestmark = pytest.mark.django_db


def create_user(username: str, role: str):
    return get_user_model().objects.create_user(username=username, password="secret123", role=role)


def build_grade_context():
    teacher_user = create_user("audit-teacher", UserRole.TEACHER)
    teacher = TeacherProfile.objects.create(user=teacher_user, personnel_number="AUD-T-001")
    group = AcademicGroup.objects.create(name="AUD-743-2", enrollment_year=2023)
    subject = Subject.objects.create(name="Аудит дисциплина", code="AUD-SEC-101")
    period = AcademicPeriod.objects.create(
        name="AUD Осенний семестр 2025",
        starts_at=date(2025, 9, 1),
        ends_at=date(2026, 1, 25),
    )
    assignment = TeachingAssignment.objects.create(teacher=teacher, subject=subject, group=group, period=period)
    student_user = create_user("audit-student", UserRole.STUDENT)
    student = StudentProfile.objects.create(user=student_user, student_id=9101, group=group)
    work = GradeWork.objects.create(
        assignment=assignment,
        title="Аудит контрольная",
        work_type="test",
        work_date=date(2025, 10, 1),
        max_score="5.00",
    )
    return teacher_user, student, work


def test_login_success_and_failure_are_audited():
    user = create_user("audit-login-user", UserRole.STUDENT)
    client = APIClient()

    failed_response = client.post(reverse("auth-login"), {"username": user.username, "password": "bad-password"})
    success_response = client.post(reverse("auth-login"), {"username": user.username, "password": "secret123"})

    assert failed_response.status_code == 400
    assert success_response.status_code == 200
    assert AuditLog.objects.filter(action=AuditAction.LOGIN_FAILED, object_id=str(user.id)).exists()
    assert AuditLog.objects.filter(action=AuditAction.LOGIN_SUCCESS, actor=user).exists()


def test_user_management_actions_are_audited():
    admin = create_user("audit-admin", UserRole.ADMIN)
    client = APIClient()
    client.force_authenticate(admin)

    create_response = client.post(
        reverse("users-list"),
        {
            "username": "audit-created-user",
            "password": "secret123",
            "role": UserRole.STUDENT,
            "phone": "+7 999-123-45-67",
        },
        format="json",
    )
    user_id = create_response.data["id"]
    update_response = client.patch(reverse("users-detail", args=[user_id]), {"first_name": "Иван"}, format="json")
    reset_response = client.post(reverse("users-reset-password", args=[user_id]), {"password": "new-secret123"})

    assert create_response.status_code == 201
    assert update_response.status_code == 200
    assert reset_response.status_code == 200
    assert AuditLog.objects.filter(action=AuditAction.USER_CREATED, actor=admin, object_id=str(user_id)).exists()
    assert AuditLog.objects.filter(action=AuditAction.USER_UPDATED, actor=admin, object_id=str(user_id)).exists()
    assert AuditLog.objects.filter(action=AuditAction.PASSWORD_RESET, actor=admin, object_id=str(user_id)).exists()


def test_grade_creation_is_audited():
    teacher_user, student, work = build_grade_context()
    client = APIClient()
    client.force_authenticate(teacher_user)

    response = client.post(reverse("grades-list"), {"work": work.id, "student": student.id, "value": "5.00"}, format="json")

    assert response.status_code == 201
    assert AuditLog.objects.filter(action=AuditAction.GRADE_CREATED, actor=teacher_user, object_id=str(response.data["id"])).exists()


def test_report_generation_is_audited(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    teacher_user, student, work = build_grade_context()
    client = APIClient()
    client.force_authenticate(teacher_user)
    client.post(reverse("grades-list"), {"work": work.id, "student": student.id, "value": "5.00"}, format="json")

    response = client.post(
        reverse("report-requests-generate"),
        {"report_type": "grades", "file_format": "csv", "parameters": {}},
        format="json",
    )

    assert response.status_code == 201
    assert AuditLog.objects.filter(
        action=AuditAction.REPORT_GENERATED,
        actor=teacher_user,
        metadata__report_type="grades",
    ).exists()


def test_audit_log_api_is_admin_only():
    admin = create_user("audit-api-admin", UserRole.ADMIN)
    student = create_user("audit-api-student", UserRole.STUDENT)
    AuditLog.objects.create(actor=admin, action=AuditAction.USER_CREATED, object_type="User", object_id=str(student.id))
    client = APIClient()

    client.force_authenticate(student)
    denied_response = client.get(reverse("audit-logs-list"))
    assert denied_response.status_code == 403

    client.force_authenticate(admin)
    allowed_response = client.get(reverse("audit-logs-list"))
    assert allowed_response.status_code == 200
    assert len(allowed_response.data) == 1
