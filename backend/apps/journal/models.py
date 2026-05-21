from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from apps.education.models import StudentProfile, TeachingAssignment


class GradeWorkType(models.TextChoices):
    CLASSWORK = "classwork", "Работа на занятии"
    HOMEWORK = "homework", "Домашняя работа"
    TEST = "test", "Контрольная работа"
    EXAM = "exam", "Экзамен"
    OTHER = "other", "Другое"


class GradeWork(models.Model):
    assignment = models.ForeignKey(
        TeachingAssignment,
        on_delete=models.CASCADE,
        related_name="grade_works",
        verbose_name="назначение преподавателя",
    )
    title = models.CharField("название работы", max_length=255)
    work_type = models.CharField("тип работы", max_length=30, choices=GradeWorkType.choices, default=GradeWorkType.CLASSWORK)
    work_date = models.DateField("дата работы")
    max_score = models.DecimalField(
        "максимальный балл",
        max_digits=5,
        decimal_places=2,
        default=Decimal("5.00"),
        validators=[MinValueValidator(Decimal("1.00"))],
    )
    weight = models.DecimalField(
        "вес",
        max_digits=5,
        decimal_places=2,
        default=Decimal("1.00"),
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_grade_works",
        verbose_name="создал",
    )
    created_at = models.DateTimeField("создано", auto_now_add=True)
    updated_at = models.DateTimeField("обновлено", auto_now=True)

    class Meta:
        verbose_name = "работа в журнале"
        verbose_name_plural = "работы в журнале"
        ordering = ("-work_date", "title")
        constraints = [
            models.UniqueConstraint(
                fields=("assignment", "title", "work_date"),
                name="unique_grade_work_assignment_title_date",
            )
        ]

    def __str__(self) -> str:
        return f"{self.title} - {self.assignment}"


class Grade(models.Model):
    work = models.ForeignKey(GradeWork, on_delete=models.CASCADE, related_name="grades", verbose_name="работа")
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="grades", verbose_name="студент")
    value = models.DecimalField(
        "оценка",
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    comment = models.TextField("комментарий", blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_grades",
        verbose_name="создал",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_grades",
        verbose_name="обновил",
    )
    created_at = models.DateTimeField("создано", auto_now_add=True)
    updated_at = models.DateTimeField("обновлено", auto_now=True)

    class Meta:
        verbose_name = "оценка"
        verbose_name_plural = "оценки"
        ordering = ("work__work_date", "student__student_id")
        constraints = [
            models.UniqueConstraint(fields=("work", "student"), name="unique_grade_work_student"),
        ]

    def __str__(self) -> str:
        return f"{self.student} - {self.work}: {self.value}"

    def clean(self) -> None:
        errors = {}
        if self.work_id and self.student_id:
            if self.student.group_id != self.work.assignment.group_id:
                errors["student"] = "Студент не входит в группу, связанную с этой работой."
            if self.value is not None and self.value > self.work.max_score:
                errors["value"] = "Оценка не может быть больше максимального балла работы."
        if errors:
            raise ValidationError(errors)


class AttendanceStatus(models.TextChoices):
    PRESENT = "present", "Присутствовал"
    ABSENT = "absent", "Отсутствовал"
    EXCUSED = "excused", "Уважительная причина"
    LATE = "late", "Опоздал"


class ClassSession(models.Model):
    assignment = models.ForeignKey(
        TeachingAssignment,
        on_delete=models.CASCADE,
        related_name="class_sessions",
        verbose_name="назначение преподавателя",
    )
    session_date = models.DateField("дата занятия")
    topic = models.CharField("тема занятия", max_length=255)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_class_sessions",
        verbose_name="создал",
    )
    created_at = models.DateTimeField("создано", auto_now_add=True)
    updated_at = models.DateTimeField("обновлено", auto_now=True)

    class Meta:
        verbose_name = "занятие"
        verbose_name_plural = "занятия"
        ordering = ("-session_date", "topic")
        constraints = [
            models.UniqueConstraint(
                fields=("assignment", "session_date", "topic"),
                name="unique_class_session_assignment_date_topic",
            )
        ]

    def __str__(self) -> str:
        return f"{self.session_date}: {self.topic} - {self.assignment}"


class AttendanceRecord(models.Model):
    session = models.ForeignKey(
        ClassSession,
        on_delete=models.CASCADE,
        related_name="attendance_records",
        verbose_name="занятие",
    )
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="attendance_records",
        verbose_name="студент",
    )
    status = models.CharField("статус", max_length=20, choices=AttendanceStatus.choices, default=AttendanceStatus.PRESENT)
    comment = models.TextField("комментарий", blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_attendance_records",
        verbose_name="создал",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_attendance_records",
        verbose_name="обновил",
    )
    created_at = models.DateTimeField("создано", auto_now_add=True)
    updated_at = models.DateTimeField("обновлено", auto_now=True)

    class Meta:
        verbose_name = "запись посещаемости"
        verbose_name_plural = "записи посещаемости"
        ordering = ("session__session_date", "student__student_id")
        constraints = [
            models.UniqueConstraint(fields=("session", "student"), name="unique_attendance_session_student"),
        ]

    def __str__(self) -> str:
        return f"{self.student} - {self.session}: {self.status}"

    def clean(self) -> None:
        if self.session_id and self.student_id and self.student.group_id != self.session.assignment.group_id:
            raise ValidationError({"student": "Студент не входит в группу, связанную с этим занятием."})
