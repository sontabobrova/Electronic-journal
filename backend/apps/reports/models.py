from django.conf import settings
from django.db import models


class ReportType(models.TextChoices):
    GRADES = "grades", "Успеваемость"
    ATTENDANCE = "attendance", "Посещаемость"


class ReportFormat(models.TextChoices):
    CSV = "csv", "CSV"
    XLSX = "xlsx", "XLSX"
    PDF = "pdf", "PDF"


class ReportRequest(models.Model):
    report_type = models.CharField("тип отчета", max_length=20, choices=ReportType.choices)
    file_format = models.CharField("формат файла", max_length=10, choices=ReportFormat.choices)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="report_requests",
        verbose_name="запросил",
    )
    parameters = models.JSONField("параметры", default=dict, blank=True)
    file = models.FileField("файл", upload_to="reports/", blank=True)
    generated_at = models.DateTimeField("дата и время формирования", auto_now_add=True)

    class Meta:
        verbose_name = "сформированный отчет"
        verbose_name_plural = "сформированные отчеты"
        ordering = ("-generated_at",)

    def __str__(self) -> str:
        return f"{self.get_report_type_display()} ({self.file_format}) от {self.generated_at:%Y-%m-%d %H:%M}"
