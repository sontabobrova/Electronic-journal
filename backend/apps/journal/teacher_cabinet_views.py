from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.education.models import StudentProfile, TeacherProfile, TeachingAssignment
from apps.users.permissions import IsTeacher

from .models import AttendanceRecord, ClassSession, Grade, GradeWork
from .teacher_cabinet_serializers import (
    TeacherAssignmentSerializer,
    TeacherAttendanceSerializer,
    TeacherCabinetProfileSerializer,
    TeacherClassSessionSerializer,
    TeacherGradeSerializer,
    TeacherGradeWorkSerializer,
    TeacherStudentSerializer,
)


def get_teacher_profile(user) -> TeacherProfile:
    try:
        return user.teacher_profile
    except TeacherProfile.DoesNotExist as exc:
        raise NotFound("Профиль преподавателя не найден.") from exc


def get_teacher_assignments(teacher: TeacherProfile):
    return TeachingAssignment.objects.filter(teacher=teacher).select_related("subject", "group", "period", "teacher__user")


class TeacherDashboardAPIView(APIView):
    permission_classes = [IsTeacher]

    def get(self, request):
        teacher = get_teacher_profile(request.user)
        assignments = get_teacher_assignments(teacher)
        assignment_ids = assignments.values_list("id", flat=True)
        group_ids = assignments.values_list("group_id", flat=True).distinct()

        grades = Grade.objects.filter(work__assignment_id__in=assignment_ids)
        attendance = AttendanceRecord.objects.filter(session__assignment_id__in=assignment_ids)
        attendance_by_status = {status: attendance.filter(status=status).count() for status in ("present", "absent", "excused", "late")}

        return Response(
            {
                "profile": TeacherCabinetProfileSerializer(teacher).data,
                "assignments_total": assignments.count(),
                "groups_total": group_ids.count(),
                "students_total": StudentProfile.objects.filter(group_id__in=group_ids).distinct().count(),
                "grade_works_total": GradeWork.objects.filter(assignment_id__in=assignment_ids).count(),
                "grades_total": grades.count(),
                "class_sessions_total": ClassSession.objects.filter(assignment_id__in=assignment_ids).count(),
                "attendance_total": attendance.count(),
                "attendance_by_status": attendance_by_status,
            }
        )


class TeacherAssignmentsAPIView(APIView):
    permission_classes = [IsTeacher]

    def get(self, request):
        teacher = get_teacher_profile(request.user)
        return Response(TeacherAssignmentSerializer(get_teacher_assignments(teacher), many=True).data)


class TeacherStudentsAPIView(APIView):
    permission_classes = [IsTeacher]

    def get(self, request):
        teacher = get_teacher_profile(request.user)
        group_ids = get_teacher_assignments(teacher).values_list("group_id", flat=True).distinct()
        students = StudentProfile.objects.filter(group_id__in=group_ids).select_related("user", "group").distinct()
        return Response(TeacherStudentSerializer(students, many=True).data)


class TeacherGradeWorksAPIView(APIView):
    permission_classes = [IsTeacher]

    def get(self, request):
        teacher = get_teacher_profile(request.user)
        assignment_ids = get_teacher_assignments(teacher).values_list("id", flat=True)
        grade_works = GradeWork.objects.filter(assignment_id__in=assignment_ids).select_related(
            "assignment__subject",
            "assignment__group",
            "assignment__period",
        )
        return Response(TeacherGradeWorkSerializer(grade_works, many=True).data)


class TeacherGradesAPIView(APIView):
    permission_classes = [IsTeacher]

    def get(self, request):
        teacher = get_teacher_profile(request.user)
        assignment_ids = get_teacher_assignments(teacher).values_list("id", flat=True)
        grades = Grade.objects.filter(work__assignment_id__in=assignment_ids).select_related(
            "student__user",
            "student__group",
            "work__assignment__subject",
            "work__assignment__group",
        )
        return Response(TeacherGradeSerializer(grades, many=True).data)


class TeacherClassSessionsAPIView(APIView):
    permission_classes = [IsTeacher]

    def get(self, request):
        teacher = get_teacher_profile(request.user)
        assignment_ids = get_teacher_assignments(teacher).values_list("id", flat=True)
        sessions = ClassSession.objects.filter(assignment_id__in=assignment_ids).select_related(
            "assignment__subject",
            "assignment__group",
            "assignment__period",
        )
        return Response(TeacherClassSessionSerializer(sessions, many=True).data)


class TeacherAttendanceAPIView(APIView):
    permission_classes = [IsTeacher]

    def get(self, request):
        teacher = get_teacher_profile(request.user)
        assignment_ids = get_teacher_assignments(teacher).values_list("id", flat=True)
        attendance = AttendanceRecord.objects.filter(session__assignment_id__in=assignment_ids).select_related(
            "student__user",
            "student__group",
            "session__assignment__subject",
            "session__assignment__group",
        )
        return Response(TeacherAttendanceSerializer(attendance, many=True).data)
