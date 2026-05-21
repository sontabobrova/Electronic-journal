from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("username", "last_name", "first_name", "email", "role", "is_active", "access_expires_at")
    list_filter = ("role", "is_active", "is_staff", "is_superuser")
    search_fields = ("username", "first_name", "last_name", "email", "phone")
    fieldsets = DjangoUserAdmin.fieldsets + (
        (
            "Профиль электронного журнала",
            {"fields": ("role", "phone", "access_expires_at", "failed_login_attempts", "locked_until")},
        ),
    )
    readonly_fields = ("failed_login_attempts", "locked_until")
