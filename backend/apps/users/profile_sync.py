from apps.education.models import TeacherProfile

from .models import UserRole


def ensure_role_profile(user) -> None:
    if user.role != UserRole.TEACHER:
        return

    TeacherProfile.objects.get_or_create(
        user=user,
        defaults={
            "personnel_number": f"T-{user.pk:06d}",
        },
    )
