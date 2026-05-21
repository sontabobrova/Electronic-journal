from django.contrib import admin

from .models import AttendanceRecord, ClassSession, Grade, GradeWork


@admin.register(GradeWork)
class GradeWorkAdmin(admin.ModelAdmin):
    list_display = ("title", "assignment", "work_type", "work_date", "max_score", "weight")
    list_filter = ("work_type", "work_date", "assignment__period", "assignment__group", "assignment__subject")
    search_fields = ("title", "assignment__subject__name", "assignment__group__name")


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("student", "work", "value", "updated_at")
    list_filter = ("work__assignment__period", "work__assignment__group", "work__assignment__subject")
    search_fields = ("student__student_id", "student__user__last_name", "work__title")


@admin.register(ClassSession)
class ClassSessionAdmin(admin.ModelAdmin):
    list_display = ("session_date", "topic", "assignment")
    list_filter = ("session_date", "assignment__period", "assignment__group", "assignment__subject")
    search_fields = ("topic", "assignment__subject__name", "assignment__group__name")


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ("student", "session", "status", "updated_at")
    list_filter = ("status", "session__assignment__period", "session__assignment__group", "session__assignment__subject")
    search_fields = ("student__student_id", "student__user__last_name", "session__topic")
