from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.users.models import UserRole


pytestmark = pytest.mark.django_db


def test_login_returns_current_user_payload():
    user = get_user_model().objects.create_user(
        username="teacher",
        password="secret123",
        role=UserRole.TEACHER,
        first_name="Иван",
        last_name="Петров",
    )

    response = APIClient().post(reverse("auth-login"), {"username": "teacher", "password": "secret123"})

    assert response.status_code == 200
    assert response.data["id"] == user.id
    assert response.data["role"] == UserRole.TEACHER
    assert response.data["permissions"]["is_teacher"] is True


def test_account_is_locked_after_three_failed_login_attempts():
    user = get_user_model().objects.create_user(username="student", password="secret123")
    client = APIClient()

    for _ in range(3):
        response = client.post(reverse("auth-login"), {"username": "student", "password": "wrong-pass"})
        assert response.status_code == 400

    user.refresh_from_db()
    assert user.failed_login_attempts == 3
    assert user.locked_until > timezone.now()

    response = client.post(reverse("auth-login"), {"username": "student", "password": "secret123"})
    assert response.status_code == 400
    assert "заблокирована" in str(response.data["detail"])


def test_admin_can_create_user_and_regular_user_cannot():
    admin = get_user_model().objects.create_user(username="admin", password="secret123", role=UserRole.ADMIN)
    student = get_user_model().objects.create_user(username="student", password="secret123", role=UserRole.STUDENT)

    payload = {
        "username": "new-teacher",
        "password": "secret123",
        "first_name": "Мария",
        "last_name": "Сидорова",
        "role": UserRole.TEACHER,
        "phone": "+7 999-123-45-67",
        "email": "teacher@example.com",
    }

    client = APIClient()
    client.force_authenticate(user=student)
    denied_response = client.post(reverse("users-list"), payload, format="json")
    assert denied_response.status_code == 403

    client.force_authenticate(user=admin)
    created_response = client.post(reverse("users-list"), payload, format="json")
    assert created_response.status_code == 201
    assert created_response.data["username"] == "new-teacher"
    assert created_response.data["role"] == UserRole.TEACHER


def test_admin_can_reset_password_and_unlock_user():
    admin = get_user_model().objects.create_user(username="admin", password="secret123", role=UserRole.ADMIN)
    user = get_user_model().objects.create_user(username="locked", password="old-secret")
    user.failed_login_attempts = 3
    user.locked_until = timezone.now() + timedelta(minutes=5)
    user.save()

    client = APIClient()
    client.force_authenticate(user=admin)
    response = client.post(reverse("users-reset-password", args=[user.id]), {"password": "new-secret123"})

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.failed_login_attempts == 0
    assert user.locked_until is None
    assert user.check_password("new-secret123")
