from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from apps.education.models import AcademicGroup, AcademicPeriod, StudentProfile, Subject, TeacherProfile, TeachingAssignment
from apps.journal.models import AttendanceRecord, ClassSession, Grade, GradeWork
from apps.users.models import UserRole


pytestmark = pytest.mark.django_db


def create_user(username: str, role: str):
    return get_user_model().objects.create_user(username=username, password="secret123", role=role)


def build_student_cabinet_data():
    teacher_user = create_user("cabinet-teacher", UserRole.TEACHER)
    teacher = TeacherProfile.objects.create(user=teacher_user, personnel_number="SC-T-001")
    group = AcademicGroup.objects.create(name="SC-743-2", enrollment_year=2023)
    subject = Subject.objects.create(name="Безопасность жизнедеятельности", code="SC-SEC-101")
    period = AcademicPeriod.objects.create(
        name="SC Осенний семестр 2025",
        starts_at=date(2025, 9, 1),
        ends_at=date(2026, 1, 25),
    )
    assignment = TeachingAssignment.objects.create(teacher=teacher, subject=subject, group=group, period=period)

    student_user = create_user("cabinet-student", UserRole.STUDENT)
    other_student_user = create_user("cabinet-other-student", UserRole.STUDENT)
    student = StudentProfile.objects.create(user=student_user, student_id=5001, group=group)
    other_student = StudentProfile.objects.create(user=other_student_user, student_id=5002, group=group)

    first_work = GradeWork.objects.create(
        assignment=assignment,
        title="Тест 1",
        work_type="test",
        work_date=date(2025, 10, 1),
        max_score="5.00",
    )
    second_work = GradeWork.objects.create(
        assignment=assignment,
        title="Тест 2",
        work_type="test",
        work_date=date(2025, 10, 15),
        max_score="5.00",
    )
    Grade.objects.create(work=first_work, student=student, value="4.00", created_by=teacher_user)
    Grade.objects.create(work=second_work, student=student, value="5.00", created_by=teacher_user)
    Grade.objects.create(work=first_work, student=other_student, value="2.00", created_by=teacher_user)

    first_session = ClassSession.objects.create(
        assignment=assignment,
        session_date=date(2025, 10, 1),
        topic="Введение",
    )
    second_session = ClassSession.objects.create(
        assignment=assignment,
        session_date=date(2025, 10, 15),
        topic="Практика",
    )
    AttendanceRecord.objects.create(session=first_session, student=student, status="present", created_by=teacher_user)
    AttendanceRecord.objects.create(session=second_session, student=student, status="absent", created_by=teacher_user)
    AttendanceRecord.objects.create(session=first_session, student=other_student, status="late", created_by=teacher_user)

    return student, teacher_user


def test_student_dashboard_returns_only_current_student_summary():
    student, _teacher_user = build_student_cabinet_data()
    client = APIClient()
    client.force_authenticate(student.user)

    response = client.get(reverse("student-dashboard"))

    assert response.status_code == 200
    assert response.data["profile"]["student_id"] == 5001
    assert response.data["grades"]["total"] == 2
    assert response.data["grades"]["average"] == "4.50"
    assert response.data["attendance"]["total"] == 2
    assert response.data["attendance"]["by_status"]["present"] == 1
    assert response.data["attendance"]["by_status"]["absent"] == 1
    assert response.data["attendance"]["by_status"]["late"] == 0


def test_student_grades_and_attendance_lists_include_only_own_records():
    student, _teacher_user = build_student_cabinet_data()
    client = APIClient()
    client.force_authenticate(student.user)

    grades_response = client.get(reverse("student-grades"))
    attendance_response = client.get(reverse("student-attendance"))

    assert grades_response.status_code == 200
    assert attendance_response.status_code == 200
    assert len(grades_response.data) == 2
    assert {item["value"] for item in grades_response.data} == {"4.00", "5.00"}
    assert len(attendance_response.data) == 2
    assert {item["status"] for item in attendance_response.data} == {"present", "absent"}


def test_non_student_cannot_access_student_cabinet():
    _student, teacher_user = build_student_cabinet_data()
    client = APIClient()
    client.force_authenticate(teacher_user)

    response = client.get(reverse("student-dashboard"))

    assert response.status_code == 403


def test_student_without_profile_receives_not_found():
    user = create_user("student-without-profile", UserRole.STUDENT)
    client = APIClient()
    client.force_authenticate(user)

    response = client.get(reverse("student-dashboard"))

    assert response.status_code == 404
    assert "Профиль студента не найден" in str(response.data)
