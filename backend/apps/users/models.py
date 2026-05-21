from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone


class UserRole(models.TextChoices):
    STUDENT = "student", "Студент"
    TEACHER = "teacher", "Преподаватель"
    ADMIN = "admin", "Администратор"


class User(AbstractUser):
    phone_validator = RegexValidator(
        regex=r"^\+7 9\d{2}-\d{3}-\d{2}-\d{2}$",
        message="Телефон должен быть в формате +7 9XX-XXX-XX-XX.",
    )

    role = models.CharField("роль", max_length=20, choices=UserRole.choices, default=UserRole.STUDENT)
    phone = models.CharField("телефон", max_length=18, validators=[phone_validator], blank=True)
    access_expires_at = models.DateTimeField("срок доступа", null=True, blank=True)
    failed_login_attempts = models.PositiveSmallIntegerField("неудачные попытки входа", default=0)
    locked_until = models.DateTimeField("заблокирован до", null=True, blank=True)

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"

    @property
    def is_student(self) -> bool:
        return self.role == UserRole.STUDENT

    @property
    def is_teacher(self) -> bool:
        return self.role == UserRole.TEACHER

    @property
    def is_system_admin(self) -> bool:
        return self.is_superuser or self.role == UserRole.ADMIN

    def has_active_access(self) -> bool:
        return self.access_expires_at is None or self.access_expires_at > timezone.now()

    def is_login_locked(self) -> bool:
        return self.locked_until is not None and self.locked_until > timezone.now()

    def register_failed_login(self) -> None:
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 3:
            self.locked_until = timezone.now() + timedelta(minutes=5)
        self.save(update_fields=["failed_login_attempts", "locked_until"])

    def reset_login_failures(self) -> None:
        if self.failed_login_attempts or self.locked_until:
            self.failed_login_attempts = 0
            self.locked_until = None
            self.save(update_fields=["failed_login_attempts", "locked_until"])
