from django.conf import settings
from django.db import models

from apps.education.models import AcademicPeriod


class NotificationType(models.TextChoices):
    SESSION_CLOSING = "session_closing", "Закрытие успеваемости"


class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="получатель",
    )
    notification_type = models.CharField("тип уведомления", max_length=50, choices=NotificationType.choices)
    title = models.CharField("заголовок", max_length=255)
    message = models.TextField("сообщение")
    period = models.ForeignKey(
        AcademicPeriod,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
        verbose_name="учебный период",
    )
    is_read = models.BooleanField("прочитано", default=False)
    created_at = models.DateTimeField("создано", auto_now_add=True)
    read_at = models.DateTimeField("прочитано в", null=True, blank=True)

    class Meta:
        verbose_name = "уведомление"
        verbose_name_plural = "уведомления"
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("recipient", "notification_type", "period"),
                name="unique_notification_recipient_type_period",
            )
        ]

    def __str__(self) -> str:
        return f"{self.recipient}: {self.title}"
