from rest_framework import serializers

from .models import ReportFormat, ReportRequest, ReportType
from .services import generate_report_file, validate_student_filter_access


class ReportRequestSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = ReportRequest
        fields = ("id", "report_type", "file_format", "parameters", "generated_at", "file", "download_url")
        read_only_fields = ("id", "generated_at", "file", "download_url")

    def get_download_url(self, report):
        request = self.context.get("request")
        if not report.file:
            return None
        url = report.file.url
        return request.build_absolute_uri(url) if request else url


class ReportGenerateSerializer(serializers.Serializer):
    report_type = serializers.ChoiceField(choices=ReportType.choices)
    file_format = serializers.ChoiceField(choices=ReportFormat.choices)
    parameters = serializers.DictField(required=False, default=dict)

    def validate(self, attrs):
        user = self.context["request"].user
        if not (user.is_system_admin or user.is_teacher or user.is_student):
            raise serializers.ValidationError("Нет прав для формирования отчета.")
        if not validate_student_filter_access(user, attrs.get("parameters", {})):
            raise serializers.ValidationError({"parameters": "Студент может формировать отчет только по своим данным."})
        return attrs

    def save(self, **kwargs):
        request = self.context["request"]
        report = ReportRequest.objects.create(
            requested_by=request.user,
            report_type=self.validated_data["report_type"],
            file_format=self.validated_data["file_format"],
            parameters=self.validated_data.get("parameters", {}),
        )
        generate_report_file(report)
        return report
