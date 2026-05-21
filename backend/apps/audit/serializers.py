from rest_framework import serializers

from apps.users.serializers import UserReadSerializer

from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    actor_details = UserReadSerializer(source="actor", read_only=True)

    class Meta:
        model = AuditLog
        fields = (
            "id",
            "actor",
            "actor_details",
            "action",
            "object_type",
            "object_id",
            "object_repr",
            "ip_address",
            "user_agent",
            "request_id",
            "metadata",
            "created_at",
        )
        read_only_fields = fields
