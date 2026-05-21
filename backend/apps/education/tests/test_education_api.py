from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from apps.education.models import AcademicGroup, AcademicPeriod, StudentProfile, Subject, TeacherProfile
from apps.users.models import UserRole


pytestmark = pytest.mark.django_db


def create_user(username: str, role: str):
    return get_user_model().objects.create_user(username=username, password="secret123", role=role)


def test_admin_can_create_group_subject_and_period():
    admin = create_user("admin", UserRole.ADMIN)
    client = APIClient()
    client.force_authenticate(admin)

    group_response = client.post(
        reverse("groups-list"),
        {"name": "743-2", "enrollment_year": 2023, "is_active": True},
        format="json",
    )
    subject_response = client.post(
        reverse("subjects-list"),
        {"name": "Информационная безопасность", "code": "IB-101", "description": ""},
        format="json",
    )
    period_response = client.post(
        reverse("periods-list"),
        {"name": "Осенний семестр 2025", "starts_at": "2025-09-01", "ends_at": "2026-01-25"},
        format="json",
    )

    assert group_response.status_code == 201
    assert subject_response.status_code == 201
    assert period_response.status_code == 201


def test_non_admin_can_read_but_cannot_create_group():
    student = create_user("student", UserRole.STUDENT)
    AcademicGroup.objects.create(name="743-2", enrollment_year=2023)
    client = APIClient()
    client.force_authenticate(student)

    list_response = client.get(reverse("groups-list"))
    create_response = client.post(reverse("groups-list"), {"name": "744-1", "enrollment_year": 2024})

    assert list_response.status_code == 200
    assert create_response.status_code == 403


def test_student_profile_requires_student_role():
    admin = create_user("admin", UserRole.ADMIN)
    teacher_user = create_user("teacher", UserRole.TEACHER)
    group = AcademicGroup.objects.create(name="743-2", enrollment_year=2023)
    client = APIClient()
    client.force_authenticate(admin)

    response = client.post(
        reverse("students-list"),
        {"user": teacher_user.id, "student_id": 1001, "group": group.id},
        format="json",
    )

    assert response.status_code == 400
    assert "user" in response.data


def test_admin_can_create_profiles_and_assignment_once():
    admin = create_user("admin", UserRole.ADMIN)
    student_user = create_user("student", UserRole.STUDENT)
    teacher_user = create_user("teacher", UserRole.TEACHER)
    group = AcademicGroup.objects.create(name="743-2", enrollment_year=2023)
    subject = Subject.objects.create(name="Информационная безопасность", code="IB-101")
    period = AcademicPeriod.objects.create(
        name="Осенний семестр 2025",
        starts_at=date(2025, 9, 1),
        ends_at=date(2026, 1, 25),
    )
    client = APIClient()
    client.force_authenticate(admin)

    student_response = client.post(
        reverse("students-list"),
        {"user": student_user.id, "student_id": 1001, "group": group.id, "enrollment_date": "2023-09-01"},
        format="json",
    )
    teacher_response = client.post(
        reverse("teachers-list"),
        {"user": teacher_user.id, "personnel_number": "T-001", "position": "Доцент"},
        format="json",
    )

    assert student_response.status_code == 201
    assert teacher_response.status_code == 201
    assert StudentProfile.objects.filter(student_id=1001).exists()
    teacher_profile = TeacherProfile.objects.get(user=teacher_user)

    payload = {
        "teacher": teacher_profile.id,
        "subject": subject.id,
        "group": group.id,
        "period": period.id,
    }
    first_response = client.post(reverse("teaching-assignments-list"), payload, format="json")
    duplicate_response = client.post(reverse("teaching-assignments-list"), payload, format="json")

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 400
    assert "Такое назначение" in str(duplicate_response.data)
