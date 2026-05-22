import pytest
from django.core.management import call_command

from apps.education.models import (
    AcademicGroup,
    AcademicPeriod,
    StudentProfile,
    Subject,
    TeacherProfile,
    TeachingAssignment,
)
from apps.journal.models import AttendanceRecord, ClassSession, Grade, GradeWork
from apps.notifications.models import Notification
from apps.users.models import User


@pytest.mark.django_db
def test_create_demo_data_command_creates_acceptance_dataset():
    call_command("create_demo_data")

    assert User.objects.filter(username__in=["admin", "teacher", "student"]).count() == 3
    assert AcademicGroup.objects.filter(name="743-2").exists()
    assert Subject.objects.filter(code="IB-101").exists()
    assert AcademicPeriod.objects.filter(name="Демо период", is_active=True).exists()
    assert TeacherProfile.objects.filter(user__username="teacher").exists()
    assert StudentProfile.objects.filter(user__username="student", group__name="743-2").exists()
    assert TeachingAssignment.objects.count() == 1
    assert GradeWork.objects.count() == 1
    assert Grade.objects.filter(student__user__username="student", value="5.00").exists()
    assert ClassSession.objects.count() == 1
    assert AttendanceRecord.objects.filter(student__user__username="student").exists()
    assert Notification.objects.filter(recipient__username="teacher").count() == 1


@pytest.mark.django_db
def test_create_demo_data_command_is_idempotent():
    call_command("create_demo_data")
    call_command("create_demo_data")

    assert User.objects.filter(username__in=["admin", "teacher", "student"]).count() == 3
    assert TeachingAssignment.objects.count() == 1
    assert GradeWork.objects.count() == 1
    assert Grade.objects.count() == 1
    assert ClassSession.objects.count() == 1
    assert AttendanceRecord.objects.count() == 1
    assert Notification.objects.count() == 1


@pytest.mark.django_db
def test_create_demo_data_full_mode_is_idempotent():
    call_command("create_demo_data", "--full")
    call_command("create_demo_data", "--full")

    assert User.objects.count() == 67
    assert AcademicGroup.objects.count() == 6
    assert Subject.objects.count() == 10
    assert AcademicPeriod.objects.count() == 3
    assert TeachingAssignment.objects.count() == 42
    assert GradeWork.objects.count() == 252
    assert Grade.objects.count() == 2520
    assert ClassSession.objects.count() == 336
    assert AttendanceRecord.objects.count() == 3360
    assert Notification.objects.count() == 6


@pytest.mark.django_db
def test_create_demo_data_reset_deletes_only_demo_records():
    User.objects.create_user(username="custom_user", password="secret123")

    call_command("create_demo_data", "--full")
    call_command("create_demo_data", "--reset", "--full")

    assert User.objects.filter(username="custom_user").exists()
    assert User.objects.count() == 68
    assert TeachingAssignment.objects.count() == 42
