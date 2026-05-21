from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.education.models import AcademicGroup, AcademicPeriod, StudentProfile, Subject, TeacherProfile, TeachingAssignment
from apps.journal.models import AttendanceRecord, ClassSession, Grade, GradeWork
from apps.users.models import UserRole


pytestmark = pytest.mark.django_db


def create_user(username: str, role: str, **extra):
    return get_user_model().objects.create_user(username=username, password="secret123", role=role, **extra)


def build_admin_cabinet_data():
    admin = create_user("admin-cabinet-admin", UserRole.ADMIN)
    teacher_user = create_user("admin-cabinet-teacher", UserRole.TEACHER)
    student_user = create_user("admin-cabinet-student", UserRole.STUDENT)
    create_user("admin-cabinet-inactive", UserRole.STUDENT, is_active=False)
    locked_user = create_user("admin-cabinet-locked", UserRole.STUDENT)
    locked_user.locked_until = timezone.now() + timedelta(minutes=5)
    locked_user.failed_login_attempts = 3
    locked_user.save(update_fields=["locked_until", "failed_login_attempts"])
    expired_user = create_user("admin-cabinet-expired", UserRole.STUDENT)
    expired_user.access_expires_at = timezone.now() - timedelta(days=1)
    expired_user.save(update_fields=["access_expires_at"])

    teacher = TeacherProfile.objects.create(user=teacher_user, personnel_number="AC-T-001")
    group = AcademicGroup.objects.create(name="AC-743-2", enrollment_year=2023)
    inactive_group = AcademicGroup.objects.create(name="AC-744-1", enrollment_year=2024, is_active=False)
    subject = Subject.objects.create(name="Админ безопасность", code="AC-SEC-101")
    Subject.objects.create(name="Архивная дисциплина", code="AC-OLD-101", is_active=False)
    period = AcademicPeriod.objects.create(
        name="AC Осенний семестр 2025",
        starts_at=date(2025, 9, 1),
        ends_at=date(2026, 1, 25),
    )
    AcademicPeriod.objects.create(
        name="AC Архивный семестр",
        starts_at=date(2024, 9, 1),
        ends_at=date(2025, 1, 25),
        is_active=False,
    )
    student = StudentProfile.objects.create(user=student_user, student_id=8001, group=group)
    assignment = TeachingAssignment.objects.create(teacher=teacher, subject=subject, group=group, period=period)

    work = GradeWork.objects.create(
        assignment=assignment,
        title="AC Контрольная",
        work_type="test",
        work_date=date(2025, 10, 1),
        max_score="5.00",
    )
    Grade.objects.create(work=work, student=student, value="5.00", created_by=teacher_user)
    session = ClassSession.objects.create(assignment=assignment, session_date=date(2025, 10, 1), topic="AC Практика")
    AttendanceRecord.objects.create(session=session, student=student, status="present", created_by=teacher_user)

    return admin, teacher_user, student_user, inactive_group


def test_admin_dashboard_returns_system_summary():
    admin, _teacher_user, _student_user, _inactive_group = build_admin_cabinet_data()
    client = APIClient()
    client.force_authenticate(admin)

    response = client.get(reverse("admin-dashboard"))

    assert response.status_code == 200
    assert response.data["users"]["total"] == 6
    assert response.data["users"]["inactive"] == 1
    assert response.data["users"]["locked"] == 1
    assert response.data["users"]["expired_access"] == 1
    assert response.data["users"]["by_role"][UserRole.ADMIN] == 1
    assert response.data["users"]["profiles"]["students"] == 1
    assert response.data["users"]["profiles"]["teachers"] == 1
    assert response.data["education"]["groups"]["total"] == 2
    assert response.data["education"]["groups"]["active"] == 1
    assert response.data["education"]["subjects"]["total"] == 2
    assert response.data["education"]["periods"]["total"] == 2
    assert response.data["education"]["teaching_assignments"] == 1
    assert response.data["journal"]["grade_works"] == 1
    assert response.data["journal"]["grades"] == 1
    assert response.data["journal"]["class_sessions"] == 1
    assert response.data["journal"]["attendance_records"] == 1
    assert response.data["journal"]["attendance_by_status"]["present"] == 1
    assert len(response.data["recent_users"]) == 5


def test_admin_summary_endpoints_are_available_to_admin():
    admin, _teacher_user, _student_user, _inactive_group = build_admin_cabinet_data()
    client = APIClient()
    client.force_authenticate(admin)

    assert client.get(reverse("admin-users-summary")).status_code == 200
    assert client.get(reverse("admin-education-summary")).status_code == 200
    assert client.get(reverse("admin-journal-summary")).status_code == 200


def test_non_admin_cannot_access_admin_cabinet():
    _admin, teacher_user, student_user, _inactive_group = build_admin_cabinet_data()
    client = APIClient()

    client.force_authenticate(teacher_user)
    teacher_response = client.get(reverse("admin-dashboard"))
    assert teacher_response.status_code == 403

    client.force_authenticate(student_user)
    student_response = client.get(reverse("admin-dashboard"))
    assert student_response.status_code == 403


def test_superuser_can_access_admin_cabinet():
    build_admin_cabinet_data()
    superuser = get_user_model().objects.create_superuser(username="root", password="secret123")
    client = APIClient()
    client.force_authenticate(superuser)

    response = client.get(reverse("admin-dashboard"))

    assert response.status_code == 200
    assert response.data["users"]["total"] == 7
