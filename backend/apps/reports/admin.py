from django.contrib import admin

from .models import ReportRequest


@admin.register(ReportRequest)
class ReportRequestAdmin(admin.ModelAdmin):
    list_display = ("report_type", "file_format", "requested_by", "generated_at", "file")
    list_filter = ("report_type", "file_format", "generated_at")
    search_fields = ("requested_by__username", "requested_by__last_name", "file")
    readonly_fields = ("generated_at",)
