from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.education.models import AcademicGroup, AcademicPeriod, StudentProfile, Subject, TeacherProfile, TeachingAssignment
from apps.journal.models import AttendanceRecord, ClassSession, Grade, GradeWork
from apps.users.models import UserRole

from .permissions import IsSystemAdmin
from .serializers import UserReadSerializer


User = get_user_model()


def get_users_summary() -> dict:
    now = timezone.now()
    return {
        "total": User.objects.count(),
        "active": User.objects.filter(is_active=True).count(),
        "inactive": User.objects.filter(is_active=False).count(),
        "locked": User.objects.filter(locked_until__gt=now).count(),
        "expired_access": User.objects.filter(access_expires_at__lte=now).count(),
        "by_role": {
            UserRole.STUDENT: User.objects.filter(role=UserRole.STUDENT).count(),
            UserRole.TEACHER: User.objects.filter(role=UserRole.TEACHER).count(),
            UserRole.ADMIN: User.objects.filter(role=UserRole.ADMIN).count(),
        },
        "profiles": {
            "students": StudentProfile.objects.count(),
            "teachers": TeacherProfile.objects.count(),
        },
    }


def get_education_summary() -> dict:
    return {
        "groups": {
            "total": AcademicGroup.objects.count(),
            "active": AcademicGroup.objects.filter(is_active=True).count(),
        },
        "subjects": {
            "total": Subject.objects.count(),
            "active": Subject.objects.filter(is_active=True).count(),
        },
        "periods": {
            "total": AcademicPeriod.objects.count(),
            "active": AcademicPeriod.objects.filter(is_active=True).count(),
        },
        "teaching_assignments": TeachingAssignment.objects.count(),
    }


def get_journal_summary() -> dict:
    attendance = AttendanceRecord.objects.all()
    return {
        "grade_works": GradeWork.objects.count(),
        "grades": Grade.objects.count(),
        "class_sessions": ClassSession.objects.count(),
        "attendance_records": attendance.count(),
        "attendance_by_status": {
            status: attendance.filter(status=status).count() for status in ("present", "absent", "excused", "late")
        },
    }


class AdminDashboardAPIView(APIView):
    permission_classes = [IsSystemAdmin]

    def get(self, request):
        recent_users = User.objects.order_by("-date_joined")[:5]
        return Response(
            {
                "users": get_users_summary(),
                "education": get_education_summary(),
                "journal": get_journal_summary(),
                "recent_users": UserReadSerializer(recent_users, many=True).data,
            }
        )


class AdminUsersSummaryAPIView(APIView):
    permission_classes = [IsSystemAdmin]

    def get(self, request):
        return Response(get_users_summary())


class AdminEducationSummaryAPIView(APIView):
    permission_classes = [IsSystemAdmin]

    def get(self, request):
        return Response(get_education_summary())


class AdminJournalSummaryAPIView(APIView):
    permission_classes = [IsSystemAdmin]

    def get(self, request):
        return Response(get_journal_summary())
