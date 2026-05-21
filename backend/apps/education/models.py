from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.users.models import UserRole


class AcademicGroup(models.Model):
    name = models.CharField("название группы", max_length=100, unique=True)
    enrollment_year = models.PositiveSmallIntegerField("год набора")
    is_active = models.BooleanField("активна", default=True)

    class Meta:
        verbose_name = "учебная группа"
        verbose_name_plural = "учебные группы"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class Subject(models.Model):
    name = models.CharField("название дисциплины", max_length=255)
    code = models.CharField("код дисциплины", max_length=50, unique=True)
    description = models.TextField("описание", blank=True)
    is_active = models.BooleanField("активна", default=True)

    class Meta:
        verbose_name = "дисциплина"
        verbose_name_plural = "дисциплины"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class AcademicPeriod(models.Model):
    name = models.CharField("название периода", max_length=100, unique=True)
    starts_at = models.DateField("дата начала")
    ends_at = models.DateField("дата окончания")
    is_active = models.BooleanField("активен", default=True)

    class Meta:
        verbose_name = "учебный период"
        verbose_name_plural = "учебные периоды"
        ordering = ("-starts_at", "name")

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        if self.ends_at < self.starts_at:
            raise ValidationError({"ends_at": "Дата окончания не может быть раньше даты начала."})


class StudentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
        verbose_name="пользователь",
    )
    student_id = models.PositiveIntegerField("ID студента", unique=True)
    group = models.ForeignKey(
        AcademicGroup,
        on_delete=models.PROTECT,
        related_name="students",
        verbose_name="группа",
    )
    enrollment_date = models.DateField("дата зачисления", null=True, blank=True)

    class Meta:
        verbose_name = "профиль студента"
        verbose_name_plural = "профили студентов"
        ordering = ("group__name", "student_id")

    def __str__(self) -> str:
        return f"{self.student_id} - {self.user.get_full_name() or self.user.username}"

    def clean(self) -> None:
        if self.user_id and self.user.role != UserRole.STUDENT:
            raise ValidationError({"user": "Профиль студента можно создать только для пользователя с ролью студента."})


class TeacherProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teacher_profile",
        verbose_name="пользователь",
    )
    personnel_number = models.CharField("табельный номер", max_length=50, unique=True)
    position = models.CharField("должность", max_length=150, blank=True)

    class Meta:
        verbose_name = "профиль преподавателя"
        verbose_name_plural = "профили преподавателей"
        ordering = ("user__last_name", "user__first_name")

    def __str__(self) -> str:
        return self.user.get_full_name() or self.user.username

    def clean(self) -> None:
        if self.user_id and self.user.role != UserRole.TEACHER:
            raise ValidationError({"user": "Профиль преподавателя можно создать только для пользователя с ролью преподавателя."})


class TeachingAssignment(models.Model):
    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE,
        related_name="assignments",
        verbose_name="преподаватель",
    )
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name="assignments", verbose_name="дисциплина")
    group = models.ForeignKey(
        AcademicGroup,
        on_delete=models.PROTECT,
        related_name="teaching_assignments",
        verbose_name="группа",
    )
    period = models.ForeignKey(
        AcademicPeriod,
        on_delete=models.PROTECT,
        related_name="teaching_assignments",
        verbose_name="учебный период",
    )

    class Meta:
        verbose_name = "назначение преподавателя"
        verbose_name_plural = "назначения преподавателей"
        ordering = ("period__starts_at", "group__name", "subject__name")
        constraints = [
            models.UniqueConstraint(
                fields=("teacher", "subject", "group", "period"),
                name="unique_teacher_subject_group_period",
            )
        ]

    def __str__(self) -> str:
        return f"{self.teacher} - {self.subject} - {self.group} ({self.period})"
