from django.conf import settings
from django.db import models


class AuditAction(models.TextChoices):
    LOGIN_SUCCESS = "login_success", "Успешный вход"
    LOGIN_FAILED = "login_failed", "Неудачный вход"
    LOGOUT = "logout", "Выход"
    USER_CREATED = "user_created", "Пользователь создан"
    USER_UPDATED = "user_updated", "Пользователь изменен"
    PASSWORD_RESET = "password_reset", "Пароль сброшен"
    GRADE_CREATED = "grade_created", "Оценка создана"
    GRADE_UPDATED = "grade_updated", "Оценка изменена"
    ATTENDANCE_CREATED = "attendance_created", "Посещаемость создана"
    ATTENDANCE_UPDATED = "attendance_updated", "Посещаемость изменена"
    REPORT_GENERATED = "report_generated", "Отчет сформирован"


class AuditLog(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        verbose_name="инициатор",
    )
    action = models.CharField("действие", max_length=50, choices=AuditAction.choices)
    object_type = models.CharField("тип объекта", max_length=100, blank=True)
    object_id = models.CharField("ID объекта", max_length=100, blank=True)
    object_repr = models.CharField("представление объекта", max_length=255, blank=True)
    ip_address = models.GenericIPAddressField("IP-адрес", null=True, blank=True)
    user_agent = models.TextField("User-Agent", blank=True)
    request_id = models.CharField("ID запроса", max_length=64, blank=True)
    metadata = models.JSONField("метаданные", default=dict, blank=True)
    created_at = models.DateTimeField("создано", auto_now_add=True)

    class Meta:
        verbose_name = "запись аудита"
        verbose_name_plural = "записи аудита"
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("action", "created_at")),
            models.Index(fields=("object_type", "object_id")),
        ]

    def __str__(self) -> str:
        return f"{self.created_at:%Y-%m-%d %H:%M:%S} {self.action}"
