from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.audit.models import AuditAction
from apps.audit.services import log_audit_event

from .models import ReportRequest
from .serializers import ReportGenerateSerializer, ReportRequestSerializer


class ReportRequestViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = ReportRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = ReportRequest.objects.select_related("requested_by")
        user = self.request.user
        if user.is_system_admin:
            return queryset
        return queryset.filter(requested_by=user)

    @action(detail=False, methods=["post"], url_path="generate")
    def generate(self, request):
        serializer = ReportGenerateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        report = serializer.save()
        log_audit_event(
            action=AuditAction.REPORT_GENERATED,
            actor=request.user,
            request=request,
            obj=report,
            metadata={"report_type": report.report_type, "file_format": report.file_format},
        )
        return Response(ReportRequestSerializer(report, context={"request": request}).data, status=201)
