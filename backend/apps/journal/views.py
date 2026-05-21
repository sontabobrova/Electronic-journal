from rest_framework import viewsets

from apps.audit.models import AuditAction
from apps.audit.services import log_audit_event

from .models import AttendanceRecord, ClassSession, Grade, GradeWork
from .permissions import IsJournalParticipant
from .serializers import AttendanceRecordSerializer, ClassSessionSerializer, GradeSerializer, GradeWorkSerializer


class GradeWorkViewSet(viewsets.ModelViewSet):
    serializer_class = GradeWorkSerializer
    permission_classes = [IsJournalParticipant]

    def get_queryset(self):
        queryset = GradeWork.objects.select_related(
            "assignment__teacher__user",
            "assignment__subject",
            "assignment__group",
            "assignment__period",
        )
        user = self.request.user
        if user.is_system_admin:
            return queryset
        if user.is_teacher:
            return queryset.filter(assignment__teacher__user=user)
        if user.is_student and hasattr(user, "student_profile"):
            return queryset.filter(assignment__group=user.student_profile.group)
        return queryset.none()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class GradeViewSet(viewsets.ModelViewSet):
    serializer_class = GradeSerializer
    permission_classes = [IsJournalParticipant]

    def get_queryset(self):
        queryset = Grade.objects.select_related(
            "work__assignment__teacher__user",
            "work__assignment__subject",
            "work__assignment__group",
            "student__user",
            "student__group",
        )
        user = self.request.user
        if user.is_system_admin:
            return queryset
        if user.is_teacher:
            return queryset.filter(work__assignment__teacher__user=user)
        if user.is_student and hasattr(user, "student_profile"):
            return queryset.filter(student=user.student_profile)
        return queryset.none()

    def perform_create(self, serializer):
        grade = serializer.save(created_by=self.request.user, updated_by=self.request.user)
        log_audit_event(action=AuditAction.GRADE_CREATED, actor=self.request.user, request=self.request, obj=grade)

    def perform_update(self, serializer):
        grade = serializer.save(updated_by=self.request.user)
        log_audit_event(action=AuditAction.GRADE_UPDATED, actor=self.request.user, request=self.request, obj=grade)


class ClassSessionViewSet(viewsets.ModelViewSet):
    serializer_class = ClassSessionSerializer
    permission_classes = [IsJournalParticipant]

    def get_queryset(self):
        queryset = ClassSession.objects.select_related(
            "assignment__teacher__user",
            "assignment__subject",
            "assignment__group",
            "assignment__period",
        )
        user = self.request.user
        if user.is_system_admin:
            return queryset
        if user.is_teacher:
            return queryset.filter(assignment__teacher__user=user)
        if user.is_student and hasattr(user, "student_profile"):
            return queryset.filter(assignment__group=user.student_profile.group)
        return queryset.none()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class AttendanceRecordViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsJournalParticipant]

    def get_queryset(self):
        queryset = AttendanceRecord.objects.select_related(
            "session__assignment__teacher__user",
            "session__assignment__subject",
            "session__assignment__group",
            "student__user",
            "student__group",
        )
        user = self.request.user
        if user.is_system_admin:
            return queryset
        if user.is_teacher:
            return queryset.filter(session__assignment__teacher__user=user)
        if user.is_student and hasattr(user, "student_profile"):
            return queryset.filter(student=user.student_profile)
        return queryset.none()

    def perform_create(self, serializer):
        record = serializer.save(created_by=self.request.user, updated_by=self.request.user)
        log_audit_event(action=AuditAction.ATTENDANCE_CREATED, actor=self.request.user, request=self.request, obj=record)

    def perform_update(self, serializer):
        record = serializer.save(updated_by=self.request.user)
        log_audit_event(action=AuditAction.ATTENDANCE_UPDATED, actor=self.request.user, request=self.request, obj=record)
