from django.utils import timezone
from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    period_name = serializers.CharField(source="period.name", read_only=True)

    class Meta:
        model = Notification
        fields = (
            "id",
            "notification_type",
            "title",
            "message",
            "period",
            "period_name",
            "is_read",
            "created_at",
            "read_at",
        )
        read_only_fields = fields


class NotificationMarkReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ("id", "is_read", "read_at")
        read_only_fields = fields

    def save(self, **kwargs):
        notification = self.instance
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save(update_fields=("is_read", "read_at"))
        return notification
