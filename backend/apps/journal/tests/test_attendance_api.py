from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from apps.education.models import AcademicGroup, AcademicPeriod, StudentProfile, Subject, TeacherProfile, TeachingAssignment
from apps.journal.models import AttendanceRecord, ClassSession
from apps.users.models import UserRole


pytestmark = pytest.mark.django_db


def create_user(username: str, role: str):
    return get_user_model().objects.create_user(username=username, password="secret123", role=role)


def build_assignment():
    teacher_user = create_user("attendance-teacher", UserRole.TEACHER)
    teacher = TeacherProfile.objects.create(user=teacher_user, personnel_number="AT-001")
    group = AcademicGroup.objects.create(name="743-2A", enrollment_year=2023)
    subject = Subject.objects.create(name="Основы безопасности", code="SEC-101")
    period = AcademicPeriod.objects.create(
        name="Весенний семестр 2026",
        starts_at=date(2026, 2, 1),
        ends_at=date(2026, 6, 30),
    )
    return TeachingAssignment.objects.create(teacher=teacher, subject=subject, group=group, period=period)


def create_student(username: str, student_id: int, group: AcademicGroup):
    user = create_user(username, UserRole.STUDENT)
    return StudentProfile.objects.create(user=user, student_id=student_id, group=group)


def test_teacher_can_create_class_session_and_attendance_record():
    assignment = build_assignment()
    student = create_student("attendance-student", 3001, assignment.group)
    client = APIClient()
    client.force_authenticate(assignment.teacher.user)

    session_response = client.post(
        reverse("class-sessions-list"),
        {
            "assignment": assignment.id,
            "session_date": "2026-03-10",
            "topic": "Вводное занятие",
        },
        format="json",
    )

    assert session_response.status_code == 201
    assert session_response.data["group_name"] == assignment.group.name

    attendance_response = client.post(
        reverse("attendance-records-list"),
        {
            "session": session_response.data["id"],
            "student": student.id,
            "status": "present",
            "comment": "На занятии",
        },
        format="json",
    )

    assert attendance_response.status_code == 201
    assert attendance_response.data["student_id_number"] == 3001
    assert AttendanceRecord.objects.get().created_by == assignment.teacher.user


def test_teacher_cannot_create_session_for_another_teacher_assignment():
    assignment = build_assignment()
    other_teacher_user = create_user("attendance-other-teacher", UserRole.TEACHER)
    TeacherProfile.objects.create(user=other_teacher_user, personnel_number="AT-002")
    client = APIClient()
    client.force_authenticate(other_teacher_user)

    response = client.post(
        reverse("class-sessions-list"),
        {"assignment": assignment.id, "session_date": "2026-03-10", "topic": "Чужое занятие"},
        format="json",
    )

    assert response.status_code == 400
    assert ClassSession.objects.count() == 0


def test_attendance_record_requires_student_from_assignment_group():
    assignment = build_assignment()
    other_group = AcademicGroup.objects.create(name="744-1A", enrollment_year=2024)
    other_student = create_student("attendance-other-student", 4001, other_group)
    session = ClassSession.objects.create(
        assignment=assignment,
        session_date=date(2026, 3, 10),
        topic="Вводное занятие",
    )
    client = APIClient()
    client.force_authenticate(assignment.teacher.user)

    response = client.post(
        reverse("attendance-records-list"),
        {"session": session.id, "student": other_student.id, "status": "absent"},
        format="json",
    )

    assert response.status_code == 400
    assert "student" in response.data


def test_student_reads_only_own_attendance_and_cannot_write():
    assignment = build_assignment()
    student = create_student("attendance-student", 3001, assignment.group)
    other_student = create_student("attendance-other-student", 3002, assignment.group)
    session = ClassSession.objects.create(
        assignment=assignment,
        session_date=date(2026, 3, 10),
        topic="Вводное занятие",
    )
    AttendanceRecord.objects.create(session=session, student=student, status="present", created_by=assignment.teacher.user)
    AttendanceRecord.objects.create(session=session, student=other_student, status="absent", created_by=assignment.teacher.user)
    client = APIClient()
    client.force_authenticate(student.user)

    list_response = client.get(reverse("attendance-records-list"))
    create_response = client.post(
        reverse("attendance-records-list"),
        {"session": session.id, "student": student.id, "status": "absent"},
    )

    assert list_response.status_code == 200
    assert len(list_response.data) == 1
    assert list_response.data[0]["student_id_number"] == 3001
    assert create_response.status_code == 403


def test_duplicate_attendance_for_same_session_and_student_is_rejected():
    assignment = build_assignment()
    student = create_student("attendance-student", 3001, assignment.group)
    session = ClassSession.objects.create(
        assignment=assignment,
        session_date=date(2026, 3, 10),
        topic="Вводное занятие",
    )
    AttendanceRecord.objects.create(session=session, student=student, status="present", created_by=assignment.teacher.user)
    client = APIClient()
    client.force_authenticate(assignment.teacher.user)

    response = client.post(
        reverse("attendance-records-list"),
        {"session": session.id, "student": student.id, "status": "absent"},
    )

    assert response.status_code == 400
    assert "уже существует" in str(response.data)
