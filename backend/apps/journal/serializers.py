from rest_framework import serializers

from apps.education.models import StudentProfile, TeachingAssignment

from .models import AttendanceRecord, ClassSession, Grade, GradeWork


class GradeWorkSerializer(serializers.ModelSerializer):
    assignment = serializers.PrimaryKeyRelatedField(queryset=TeachingAssignment.objects.select_related("teacher__user").all())
    subject_name = serializers.CharField(source="assignment.subject.name", read_only=True)
    group_name = serializers.CharField(source="assignment.group.name", read_only=True)
    period_name = serializers.CharField(source="assignment.period.name", read_only=True)
    teacher_name = serializers.CharField(source="assignment.teacher.user.get_full_name", read_only=True)

    class Meta:
        model = GradeWork
        fields = (
            "id",
            "assignment",
            "subject_name",
            "group_name",
            "period_name",
            "teacher_name",
            "title",
            "work_type",
            "work_date",
            "max_score",
            "weight",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.user.is_authenticated and request.user.is_teacher and not request.user.is_system_admin:
            self.fields["assignment"].queryset = self.fields["assignment"].queryset.filter(teacher__user=request.user)


class GradeSerializer(serializers.ModelSerializer):
    work = serializers.PrimaryKeyRelatedField(queryset=GradeWork.objects.select_related("assignment").all())
    student = serializers.PrimaryKeyRelatedField(queryset=StudentProfile.objects.select_related("user", "group").all())
    student_id_number = serializers.IntegerField(source="student.student_id", read_only=True)
    student_name = serializers.CharField(source="student.user.get_full_name", read_only=True)
    work_title = serializers.CharField(source="work.title", read_only=True)
    subject_name = serializers.CharField(source="work.assignment.subject.name", read_only=True)
    group_name = serializers.CharField(source="work.assignment.group.name", read_only=True)

    class Meta:
        model = Grade
        fields = (
            "id",
            "work",
            "work_title",
            "subject_name",
            "group_name",
            "student",
            "student_id_number",
            "student_name",
            "value",
            "comment",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Grade.objects.all(),
                fields=("work", "student"),
                message="Оценка для этого студента по этой работе уже существует.",
            )
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.user.is_authenticated and request.user.is_teacher and not request.user.is_system_admin:
            self.fields["work"].queryset = self.fields["work"].queryset.filter(assignment__teacher__user=request.user)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        work = attrs.get("work", getattr(self.instance, "work", None))
        student = attrs.get("student", getattr(self.instance, "student", None))
        value = attrs.get("value", getattr(self.instance, "value", None))

        if work and student and student.group_id != work.assignment.group_id:
            raise serializers.ValidationError({"student": "Студент не входит в группу, связанную с этой работой."})
        if work and value is not None and value > work.max_score:
            raise serializers.ValidationError({"value": "Оценка не может быть больше максимального балла работы."})
        return attrs


class ClassSessionSerializer(serializers.ModelSerializer):
    assignment = serializers.PrimaryKeyRelatedField(queryset=TeachingAssignment.objects.select_related("teacher__user").all())
    subject_name = serializers.CharField(source="assignment.subject.name", read_only=True)
    group_name = serializers.CharField(source="assignment.group.name", read_only=True)
    period_name = serializers.CharField(source="assignment.period.name", read_only=True)
    teacher_name = serializers.CharField(source="assignment.teacher.user.get_full_name", read_only=True)

    class Meta:
        model = ClassSession
        fields = (
            "id",
            "assignment",
            "subject_name",
            "group_name",
            "period_name",
            "teacher_name",
            "session_date",
            "topic",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.user.is_authenticated and request.user.is_teacher and not request.user.is_system_admin:
            self.fields["assignment"].queryset = self.fields["assignment"].queryset.filter(teacher__user=request.user)


class AttendanceRecordSerializer(serializers.ModelSerializer):
    session = serializers.PrimaryKeyRelatedField(queryset=ClassSession.objects.select_related("assignment").all())
    student = serializers.PrimaryKeyRelatedField(queryset=StudentProfile.objects.select_related("user", "group").all())
    student_id_number = serializers.IntegerField(source="student.student_id", read_only=True)
    student_name = serializers.CharField(source="student.user.get_full_name", read_only=True)
    session_topic = serializers.CharField(source="session.topic", read_only=True)
    session_date = serializers.DateField(source="session.session_date", read_only=True)
    subject_name = serializers.CharField(source="session.assignment.subject.name", read_only=True)
    group_name = serializers.CharField(source="session.assignment.group.name", read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = (
            "id",
            "session",
            "session_topic",
            "session_date",
            "subject_name",
            "group_name",
            "student",
            "student_id_number",
            "student_name",
            "status",
            "comment",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=AttendanceRecord.objects.all(),
                fields=("session", "student"),
                message="Отметка посещаемости для этого студента по этому занятию уже существует.",
            )
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.user.is_authenticated and request.user.is_teacher and not request.user.is_system_admin:
            self.fields["session"].queryset = self.fields["session"].queryset.filter(assignment__teacher__user=request.user)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        session = attrs.get("session", getattr(self.instance, "session", None))
        student = attrs.get("student", getattr(self.instance, "student", None))

        if session and student and student.group_id != session.assignment.group_id:
            raise serializers.ValidationError({"student": "Студент не входит в группу, связанную с этим занятием."})
        return attrs
