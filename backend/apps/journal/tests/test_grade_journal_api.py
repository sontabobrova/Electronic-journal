from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from apps.education.models import AcademicGroup, AcademicPeriod, StudentProfile, Subject, TeacherProfile, TeachingAssignment
from apps.journal.models import Grade, GradeWork
from apps.users.models import UserRole


pytestmark = pytest.mark.django_db


def create_user(username: str, role: str):
    return get_user_model().objects.create_user(username=username, password="secret123", role=role)


def build_assignment():
    teacher_user = create_user("teacher", UserRole.TEACHER)
    teacher = TeacherProfile.objects.create(user=teacher_user, personnel_number="T-001")
    group = AcademicGroup.objects.create(name="743-2", enrollment_year=2023)
    subject = Subject.objects.create(name="Информационная безопасность", code="IB-101")
    period = AcademicPeriod.objects.create(
        name="Осенний семестр 2025",
        starts_at=date(2025, 9, 1),
        ends_at=date(2026, 1, 25),
    )
    assignment = TeachingAssignment.objects.create(teacher=teacher, subject=subject, group=group, period=period)
    return assignment


def create_student(username: str, student_id: int, group: AcademicGroup):
    user = create_user(username, UserRole.STUDENT)
    return StudentProfile.objects.create(user=user, student_id=student_id, group=group)


def test_teacher_can_create_grade_work_and_grade_for_own_assignment():
    assignment = build_assignment()
    student = create_student("student", 1001, assignment.group)
    client = APIClient()
    client.force_authenticate(assignment.teacher.user)

    work_response = client.post(
        reverse("grade-works-list"),
        {
            "assignment": assignment.id,
            "title": "Контрольная работа 1",
            "work_type": "test",
            "work_date": "2025-10-15",
            "max_score": "5.00",
            "weight": "1.00",
        },
        format="json",
    )

    assert work_response.status_code == 201
    assert work_response.data["subject_name"] == assignment.subject.name

    grade_response = client.post(
        reverse("grades-list"),
        {"work": work_response.data["id"], "student": student.id, "value": "4.00", "comment": "Хорошая работа"},
        format="json",
    )

    assert grade_response.status_code == 201
    assert grade_response.data["student_id_number"] == 1001
    assert Grade.objects.get().created_by == assignment.teacher.user


def test_teacher_cannot_create_grade_work_for_another_teacher_assignment():
    assignment = build_assignment()
    other_teacher_user = create_user("other-teacher", UserRole.TEACHER)
    TeacherProfile.objects.create(user=other_teacher_user, personnel_number="T-002")
    client = APIClient()
    client.force_authenticate(other_teacher_user)

    response = client.post(
        reverse("grade-works-list"),
        {
            "assignment": assignment.id,
            "title": "Чужая работа",
            "work_type": "test",
            "work_date": "2025-10-15",
            "max_score": "5.00",
            "weight": "1.00",
        },
        format="json",
    )

    assert response.status_code == 400
    assert GradeWork.objects.count() == 0


def test_grade_requires_student_from_assignment_group_and_valid_score():
    assignment = build_assignment()
    other_group = AcademicGroup.objects.create(name="744-1", enrollment_year=2024)
    other_student = create_student("other-student", 2001, other_group)
    work = GradeWork.objects.create(
        assignment=assignment,
        title="Контрольная работа 1",
        work_type="test",
        work_date=date(2025, 10, 15),
        max_score="5.00",
    )
    client = APIClient()
    client.force_authenticate(assignment.teacher.user)

    wrong_group_response = client.post(
        reverse("grades-list"),
        {"work": work.id, "student": other_student.id, "value": "4.00"},
        format="json",
    )
    too_high_score_response = client.post(
        reverse("grades-list"),
        {"work": work.id, "student": create_student("student", 1001, assignment.group).id, "value": "6.00"},
        format="json",
    )

    assert wrong_group_response.status_code == 400
    assert "student" in wrong_group_response.data
    assert too_high_score_response.status_code == 400
    assert "value" in too_high_score_response.data


def test_student_reads_only_own_grades_and_cannot_write():
    assignment = build_assignment()
    student = create_student("student", 1001, assignment.group)
    other_student = create_student("other-student", 1002, assignment.group)
    work = GradeWork.objects.create(
        assignment=assignment,
        title="Контрольная работа 1",
        work_type="test",
        work_date=date(2025, 10, 15),
        max_score="5.00",
    )
    Grade.objects.create(work=work, student=student, value="5.00", created_by=assignment.teacher.user)
    Grade.objects.create(work=work, student=other_student, value="3.00", created_by=assignment.teacher.user)

    client = APIClient()
    client.force_authenticate(student.user)

    list_response = client.get(reverse("grades-list"))
    create_response = client.post(reverse("grades-list"), {"work": work.id, "student": student.id, "value": "4.00"})

    assert list_response.status_code == 200
    assert len(list_response.data) == 1
    assert list_response.data[0]["student_id_number"] == 1001
    assert create_response.status_code == 403


def test_duplicate_grade_for_same_work_and_student_is_rejected():
    assignment = build_assignment()
    student = create_student("student", 1001, assignment.group)
    work = GradeWork.objects.create(
        assignment=assignment,
        title="Контрольная работа 1",
        work_type="test",
        work_date=date(2025, 10, 15),
        max_score="5.00",
    )
    Grade.objects.create(work=work, student=student, value="4.00", created_by=assignment.teacher.user)
    client = APIClient()
    client.force_authenticate(assignment.teacher.user)

    response = client.post(reverse("grades-list"), {"work": work.id, "student": student.id, "value": "5.00"})

    assert response.status_code == 400
    assert "уже существует" in str(response.data)
