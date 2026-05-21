from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .student_cabinet_views import StudentAttendanceAPIView, StudentDashboardAPIView, StudentGradesAPIView
from .teacher_cabinet_views import (
    TeacherAssignmentsAPIView,
    TeacherAttendanceAPIView,
    TeacherClassSessionsAPIView,
    TeacherDashboardAPIView,
    TeacherGradesAPIView,
    TeacherGradeWorksAPIView,
    TeacherStudentsAPIView,
)
from .views import AttendanceRecordViewSet, ClassSessionViewSet, GradeViewSet, GradeWorkViewSet


router = DefaultRouter()
router.register("grade-works", GradeWorkViewSet, basename="grade-works")
router.register("grades", GradeViewSet, basename="grades")
router.register("class-sessions", ClassSessionViewSet, basename="class-sessions")
router.register("attendance-records", AttendanceRecordViewSet, basename="attendance-records")

urlpatterns = [
    path("student/dashboard/", StudentDashboardAPIView.as_view(), name="student-dashboard"),
    path("student/grades/", StudentGradesAPIView.as_view(), name="student-grades"),
    path("student/attendance/", StudentAttendanceAPIView.as_view(), name="student-attendance"),
    path("teacher/dashboard/", TeacherDashboardAPIView.as_view(), name="teacher-dashboard"),
    path("teacher/assignments/", TeacherAssignmentsAPIView.as_view(), name="teacher-assignments"),
    path("teacher/students/", TeacherStudentsAPIView.as_view(), name="teacher-students"),
    path("teacher/grade-works/", TeacherGradeWorksAPIView.as_view(), name="teacher-grade-works"),
    path("teacher/grades/", TeacherGradesAPIView.as_view(), name="teacher-grades"),
    path("teacher/class-sessions/", TeacherClassSessionsAPIView.as_view(), name="teacher-class-sessions"),
    path("teacher/attendance/", TeacherAttendanceAPIView.as_view(), name="teacher-attendance"),
    path("", include(router.urls)),
]
