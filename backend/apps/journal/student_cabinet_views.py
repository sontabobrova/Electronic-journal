from decimal import Decimal, ROUND_HALF_UP

from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.education.models import StudentProfile
from apps.users.permissions import IsStudent

from .models import AttendanceRecord, Grade
from .student_cabinet_serializers import (
    StudentCabinetAttendanceSerializer,
    StudentCabinetGradeSerializer,
    StudentCabinetProfileSerializer,
)


def get_student_profile(user) -> StudentProfile:
    try:
        return user.student_profile
    except StudentProfile.DoesNotExist as exc:
        raise NotFound("Профиль студента не найден.") from exc


def decimal_average(values) -> Decimal | None:
    values = list(values)
    if not values:
        return None
    total = sum(values, Decimal("0.00"))
    return (total / len(values)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class StudentDashboardAPIView(APIView):
    permission_classes = [IsStudent]

    def get(self, request):
        student = get_student_profile(request.user)
        grades = Grade.objects.filter(student=student).select_related("work__assignment__subject")
        attendance = AttendanceRecord.objects.filter(student=student)
        attendance_by_status = {status: attendance.filter(status=status).count() for status in ("present", "absent", "excused", "late")}

        return Response(
            {
                "profile": StudentCabinetProfileSerializer(student).data,
                "grades": {
                    "total": grades.count(),
                    "average": str(average) if (average := decimal_average(grades.values_list("value", flat=True))) is not None else None,
                },
                "attendance": {
                    "total": attendance.count(),
                    "by_status": attendance_by_status,
                },
            }
        )


class StudentGradesAPIView(APIView):
    permission_classes = [IsStudent]

    def get(self, request):
        student = get_student_profile(request.user)
        queryset = Grade.objects.filter(student=student).select_related(
            "work__assignment__subject",
            "work__assignment__period",
            "work__assignment__teacher__user",
        )
        return Response(StudentCabinetGradeSerializer(queryset, many=True).data)


class StudentAttendanceAPIView(APIView):
    permission_classes = [IsStudent]

    def get(self, request):
        student = get_student_profile(request.user)
        queryset = AttendanceRecord.objects.filter(student=student).select_related(
            "session__assignment__subject",
            "session__assignment__period",
            "session__assignment__teacher__user",
        )
        return Response(StudentCabinetAttendanceSerializer(queryset, many=True).data)
