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


def create_assignment(prefix: str):
    teacher_user = create_user(f"{prefix}-teacher", UserRole.TEACHER)
    teacher = TeacherProfile.objects.create(user=teacher_user, personnel_number=f"{prefix}-T-001")
    group = AcademicGroup.objects.create(name=f"{prefix}-743-2", enrollment_year=2023)
    subject = Subject.objects.create(name=f"{prefix} Безопасность", code=f"{prefix}-SEC-101")
    period = AcademicPeriod.objects.create(
        name=f"{prefix} Осенний семестр 2025",
        starts_at=date(2025, 9, 1),
        ends_at=date(2026, 1, 25),
    )
    assignment = TeachingAssignment.objects.create(teacher=teacher, subject=subject, group=group, period=period)
    return teacher, assignment


def create_student(username: str, student_id: int, group: AcademicGroup):
    user = create_user(username, UserRole.STUDENT)
    return StudentProfile.objects.create(user=user, student_id=student_id, group=group)


def build_teacher_cabinet_data():
    teacher, assignment = create_assignment("main")
    other_teacher, other_assignment = create_assignment("other")
    student = create_student("teacher-cabinet-student", 6001, assignment.group)
    other_student = create_student("teacher-cabinet-other-student", 7001, other_assignment.group)

    work = GradeWork.objects.create(
        assignment=assignment,
        title="Контрольная",
        work_type="test",
        work_date=date(2025, 10, 1),
        max_score="5.00",
    )
    other_work = GradeWork.objects.create(
        assignment=other_assignment,
        title="Чужая контрольная",
        work_type="test",
        work_date=date(2025, 10, 1),
        max_score="5.00",
    )
    Grade.objects.create(work=work, student=student, value="5.00", created_by=teacher.user)
    Grade.objects.create(work=other_work, student=other_student, value="2.00", created_by=other_teacher.user)

    session = ClassSession.objects.create(
        assignment=assignment,
        session_date=date(2025, 10, 1),
        topic="Практика",
    )
    other_session = ClassSession.objects.create(
        assignment=other_assignment,
        session_date=date(2025, 10, 1),
        topic="Чужая практика",
    )
    AttendanceRecord.objects.create(session=session, student=student, status="present", created_by=teacher.user)
    AttendanceRecord.objects.create(session=other_session, student=other_student, status="absent", created_by=other_teacher.user)

    return teacher, other_teacher


def test_teacher_dashboard_returns_only_own_summary():
    teacher, _other_teacher = build_teacher_cabinet_data()
    client = APIClient()
    client.force_authenticate(teacher.user)

    response = client.get(reverse("teacher-dashboard"))

    assert response.status_code == 200
    assert response.data["profile"]["personnel_number"] == "main-T-001"
    assert response.data["assignments_total"] == 1
    assert response.data["groups_total"] == 1
    assert response.data["students_total"] == 1
    assert response.data["grade_works_total"] == 1
    assert response.data["grades_total"] == 1
    assert response.data["class_sessions_total"] == 1
    assert response.data["attendance_total"] == 1
    assert response.data["attendance_by_status"]["present"] == 1
    assert response.data["attendance_by_status"]["absent"] == 0


def test_teacher_lists_include_only_own_assignments_and_records():
    teacher, _other_teacher = build_teacher_cabinet_data()
    client = APIClient()
    client.force_authenticate(teacher.user)

    assignments_response = client.get(reverse("teacher-assignments"))
    students_response = client.get(reverse("teacher-students"))
    grade_works_response = client.get(reverse("teacher-grade-works"))
    grades_response = client.get(reverse("teacher-grades"))
    sessions_response = client.get(reverse("teacher-class-sessions"))
    attendance_response = client.get(reverse("teacher-attendance"))

    assert assignments_response.status_code == 200
    assert len(assignments_response.data) == 1
    assert assignments_response.data[0]["subject_code"] == "main-SEC-101"
    assert len(students_response.data) == 1
    assert students_response.data[0]["student_id"] == 6001
    assert len(grade_works_response.data) == 1
    assert grade_works_response.data[0]["title"] == "Контрольная"
    assert len(grades_response.data) == 1
    assert grades_response.data[0]["student_id_number"] == 6001
    assert len(sessions_response.data) == 1
    assert sessions_response.data[0]["topic"] == "Практика"
    assert len(attendance_response.data) == 1
    assert attendance_response.data[0]["status"] == "present"


def test_non_teacher_cannot_access_teacher_cabinet():
    _teacher, _other_teacher = build_teacher_cabinet_data()
    student_user = create_user("not-teacher-student", UserRole.STUDENT)
    client = APIClient()
    client.force_authenticate(student_user)

    response = client.get(reverse("teacher-dashboard"))

    assert response.status_code == 403


def test_teacher_without_profile_receives_not_found():
    teacher_user = create_user("teacher-without-profile", UserRole.TEACHER)
    client = APIClient()
    client.force_authenticate(teacher_user)

    response = client.get(reverse("teacher-dashboard"))

    assert response.status_code == 404
    assert "Профиль преподавателя не найден" in str(response.data)
