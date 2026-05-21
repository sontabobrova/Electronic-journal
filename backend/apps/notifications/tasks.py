from celery import shared_task
from django.utils import timezone

from apps.education.models import AcademicPeriod, TeachingAssignment

from .models import Notification, NotificationType


@shared_task
def send_session_closing_reminders() -> int:
    target_date = timezone.localdate() + timezone.timedelta(days=3)
    periods = AcademicPeriod.objects.filter(is_active=True, ends_at=target_date)
    created_count = 0

    for period in periods:
        teacher_ids = (
            TeachingAssignment.objects.filter(period=period)
            .values_list("teacher__user_id", flat=True)
            .distinct()
        )
        for teacher_id in teacher_ids:
            _notification, created = Notification.objects.get_or_create(
                recipient_id=teacher_id,
                notification_type=NotificationType.SESSION_CLOSING,
                period=period,
                defaults={
                    "title": "Необходимо закрыть успеваемость",
                    "message": f"До окончания периода «{period.name}» осталось 3 дня. Проверьте и закройте успеваемость.",
                },
            )
            if created:
                created_count += 1
    return created_count
