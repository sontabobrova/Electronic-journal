from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.education.models import AcademicGroup, AcademicPeriod, Subject, TeacherProfile, TeachingAssignment
from apps.notifications.models import Notification, NotificationType
from apps.notifications.tasks import send_session_closing_reminders
from apps.users.models import UserRole


pytestmark = pytest.mark.django_db


def create_user(username: str, role: str):
    return get_user_model().objects.create_user(username=username, password="secret123", role=role)


def create_assignment_for_period(username: str, period: AcademicPeriod):
    teacher_user = create_user(username, UserRole.TEACHER)
    teacher = TeacherProfile.objects.create(user=teacher_user, personnel_number=f"{username}-T")
    group = AcademicGroup.objects.create(name=f"{username}-743-2", enrollment_year=2023)
    subject = Subject.objects.create(name=f"{username} дисциплина", code=f"{username}-SEC")
    TeachingAssignment.objects.create(teacher=teacher, subject=subject, group=group, period=period)
    return teacher_user


def test_session_closing_reminder_created_three_days_before_period_end(monkeypatch):
    today = date(2026, 5, 22)
    monkeypatch.setattr(timezone, "localdate", lambda: today)
    target_period = AcademicPeriod.objects.create(
        name="Целевой период",
        starts_at=today - timedelta(days=30),
        ends_at=today + timedelta(days=3),
    )
    non_target_period = AcademicPeriod.objects.create(
        name="Дальний период",
        starts_at=today - timedelta(days=30),
        ends_at=today + timedelta(days=4),
    )
    first_teacher = create_assignment_for_period("reminder-first", target_period)
    second_teacher = create_assignment_for_period("reminder-second", target_period)
    create_assignment_for_period("reminder-third", non_target_period)

    created_count = send_session_closing_reminders()
    duplicate_count = send_session_closing_reminders()

    assert created_count == 2
    assert duplicate_count == 0
    assert Notification.objects.count() == 2
    assert Notification.objects.filter(recipient=first_teacher, period=target_period).exists()
    assert Notification.objects.filter(recipient=second_teacher, period=target_period).exists()
    assert Notification.objects.filter(period=non_target_period).count() == 0
    assert Notification.objects.first().notification_type == NotificationType.SESSION_CLOSING


def test_teacher_sees_only_own_notifications_and_can_mark_read(monkeypatch):
    today = date(2026, 5, 22)
    monkeypatch.setattr(timezone, "localdate", lambda: today)
    period = AcademicPeriod.objects.create(
        name="Период уведомлений",
        starts_at=today - timedelta(days=30),
        ends_at=today + timedelta(days=3),
    )
    teacher = create_assignment_for_period("notify-teacher", period)
    other_teacher = create_assignment_for_period("notify-other-teacher", period)
    send_session_closing_reminders()

    client = APIClient()
    client.force_authenticate(teacher)
    list_response = client.get(reverse("notifications-list"))

    assert list_response.status_code == 200
    assert len(list_response.data) == 1
    assert list_response.data[0]["is_read"] is False
    assert Notification.objects.filter(recipient=other_teacher).exists()

    mark_response = client.post(reverse("notifications-mark-read", args=[list_response.data[0]["id"]]))
    assert mark_response.status_code == 200
    assert mark_response.data["is_read"] is True
    assert mark_response.data["read_at"] is not None


def test_admin_sees_all_notifications(monkeypatch):
    today = date(2026, 5, 22)
    monkeypatch.setattr(timezone, "localdate", lambda: today)
    period = AcademicPeriod.objects.create(
        name="Админ период уведомлений",
        starts_at=today - timedelta(days=30),
        ends_at=today + timedelta(days=3),
    )
    create_assignment_for_period("admin-notify-first", period)
    create_assignment_for_period("admin-notify-second", period)
    send_session_closing_reminders()
    admin = create_user("notification-admin", UserRole.ADMIN)
    client = APIClient()
    client.force_authenticate(admin)

    response = client.get(reverse("notifications-list"))

    assert response.status_code == 200
    assert len(response.data) == 2


def test_student_does_not_receive_teacher_reminders(monkeypatch):
    today = date(2026, 5, 22)
    monkeypatch.setattr(timezone, "localdate", lambda: today)
    period = AcademicPeriod.objects.create(
        name="Студенческий период уведомлений",
        starts_at=today - timedelta(days=30),
        ends_at=today + timedelta(days=3),
    )
    create_assignment_for_period("student-reminder-teacher", period)
    send_session_closing_reminders()
    student = create_user("notification-student", UserRole.STUDENT)
    client = APIClient()
    client.force_authenticate(student)

    response = client.get(reverse("notifications-list"))

    assert response.status_code == 200
    assert response.data == []
