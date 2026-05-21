from rest_framework import serializers

from apps.education.models import StudentProfile

from .models import AttendanceRecord, Grade


class StudentCabinetProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.get_full_name", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    group_name = serializers.CharField(source="group.name", read_only=True)

    class Meta:
        model = StudentProfile
        fields = ("id", "student_id", "full_name", "username", "email", "group", "group_name", "enrollment_date")


class StudentCabinetGradeSerializer(serializers.ModelSerializer):
    work_title = serializers.CharField(source="work.title", read_only=True)
    work_type = serializers.CharField(source="work.work_type", read_only=True)
    work_date = serializers.DateField(source="work.work_date", read_only=True)
    max_score = serializers.DecimalField(source="work.max_score", max_digits=5, decimal_places=2, read_only=True)
    subject_name = serializers.CharField(source="work.assignment.subject.name", read_only=True)
    period_name = serializers.CharField(source="work.assignment.period.name", read_only=True)
    teacher_name = serializers.CharField(source="work.assignment.teacher.user.get_full_name", read_only=True)

    class Meta:
        model = Grade
        fields = (
            "id",
            "value",
            "comment",
            "work_title",
            "work_type",
            "work_date",
            "max_score",
            "subject_name",
            "period_name",
            "teacher_name",
            "updated_at",
        )


class StudentCabinetAttendanceSerializer(serializers.ModelSerializer):
    session_topic = serializers.CharField(source="session.topic", read_only=True)
    session_date = serializers.DateField(source="session.session_date", read_only=True)
    subject_name = serializers.CharField(source="session.assignment.subject.name", read_only=True)
    period_name = serializers.CharField(source="session.assignment.period.name", read_only=True)
    teacher_name = serializers.CharField(source="session.assignment.teacher.user.get_full_name", read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = (
            "id",
            "status",
            "comment",
            "session_topic",
            "session_date",
            "subject_name",
            "period_name",
            "teacher_name",
            "updated_at",
        )
