from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "action", "actor", "object_type", "object_id", "ip_address")
    list_filter = ("action", "created_at")
    search_fields = ("actor__username", "object_type", "object_id", "object_repr", "request_id")
    readonly_fields = (
        "actor",
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
