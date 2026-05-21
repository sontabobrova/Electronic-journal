from django.contrib import admin

from .models import AcademicGroup, AcademicPeriod, StudentProfile, Subject, TeacherProfile, TeachingAssignment


@admin.register(AcademicGroup)
class AcademicGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "enrollment_year", "is_active")
    list_filter = ("is_active", "enrollment_year")
    search_fields = ("name",)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "code")


@admin.register(AcademicPeriod)
class AcademicPeriodAdmin(admin.ModelAdmin):
    list_display = ("name", "starts_at", "ends_at", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("student_id", "user", "group", "enrollment_date")
    list_filter = ("group",)
    search_fields = ("student_id", "user__username", "user__first_name", "user__last_name")


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "personnel_number", "position")
    search_fields = ("personnel_number", "user__username", "user__first_name", "user__last_name")


@admin.register(TeachingAssignment)
class TeachingAssignmentAdmin(admin.ModelAdmin):
    list_display = ("teacher", "subject", "group", "period")
    list_filter = ("period", "group", "subject")
    search_fields = ("teacher__user__username", "teacher__user__last_name", "subject__name", "group__name")
