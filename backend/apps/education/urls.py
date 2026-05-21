from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AcademicGroupViewSet,
    AcademicPeriodViewSet,
    StudentProfileViewSet,
    SubjectViewSet,
    TeacherProfileViewSet,
    TeachingAssignmentViewSet,
)


router = DefaultRouter()
router.register("groups", AcademicGroupViewSet, basename="groups")
router.register("subjects", SubjectViewSet, basename="subjects")
router.register("periods", AcademicPeriodViewSet, basename="periods")
router.register("students", StudentProfileViewSet, basename="students")
router.register("teachers", TeacherProfileViewSet, basename="teachers")
router.register("teaching-assignments", TeachingAssignmentViewSet, basename="teaching-assignments")

urlpatterns = [
    path("", include(router.urls)),
]
