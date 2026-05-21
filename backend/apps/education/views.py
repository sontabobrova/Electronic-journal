from rest_framework import viewsets

from .models import AcademicGroup, AcademicPeriod, StudentProfile, Subject, TeacherProfile, TeachingAssignment
from .permissions import IsAdminOrReadOnlyAuthenticated
from .serializers import (
    AcademicGroupSerializer,
    AcademicPeriodSerializer,
    StudentProfileSerializer,
    SubjectSerializer,
    TeacherProfileSerializer,
    TeachingAssignmentSerializer,
)


class AcademicGroupViewSet(viewsets.ModelViewSet):
    queryset = AcademicGroup.objects.all()
    serializer_class = AcademicGroupSerializer
    permission_classes = [IsAdminOrReadOnlyAuthenticated]


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAdminOrReadOnlyAuthenticated]


class AcademicPeriodViewSet(viewsets.ModelViewSet):
    queryset = AcademicPeriod.objects.all()
    serializer_class = AcademicPeriodSerializer
    permission_classes = [IsAdminOrReadOnlyAuthenticated]


class StudentProfileViewSet(viewsets.ModelViewSet):
    queryset = StudentProfile.objects.select_related("user", "group").all()
    serializer_class = StudentProfileSerializer
    permission_classes = [IsAdminOrReadOnlyAuthenticated]


class TeacherProfileViewSet(viewsets.ModelViewSet):
    queryset = TeacherProfile.objects.select_related("user").all()
    serializer_class = TeacherProfileSerializer
    permission_classes = [IsAdminOrReadOnlyAuthenticated]


class TeachingAssignmentViewSet(viewsets.ModelViewSet):
    queryset = TeachingAssignment.objects.select_related("teacher__user", "subject", "group", "period").all()
    serializer_class = TeachingAssignmentSerializer
    permission_classes = [IsAdminOrReadOnlyAuthenticated]
