from rest_framework import serializers

from apps.education.models import StudentProfile, TeacherProfile, TeachingAssignment

from .models import AttendanceRecord, ClassSession, Grade, GradeWork


class TeacherCabinetProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.get_full_name", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = TeacherProfile
        fields = ("id", "full_name", "username", "email", "personnel_number", "position")


class TeacherAssignmentSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    subject_code = serializers.CharField(source="subject.code", read_only=True)
    group_name = serializers.CharField(source="group.name", read_only=True)
    period_name = serializers.CharField(source="period.name", read_only=True)

    class Meta:
        model = TeachingAssignment
        fields = ("id", "subject", "subject_name", "subject_code", "group", "group_name", "period", "period_name")


class TeacherStudentSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.get_full_name", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    group_name = serializers.CharField(source="group.name", read_only=True)

    class Meta:
        model = StudentProfile
        fields = ("id", "student_id", "full_name", "username", "group", "group_name", "enrollment_date")


class TeacherGradeWorkSerializer(serializers.ModelSerializer):
    assignment_id = serializers.IntegerField(source="assignment.id", read_only=True)
    subject_name = serializers.CharField(source="assignment.subject.name", read_only=True)
    group_name = serializers.CharField(source="assignment.group.name", read_only=True)
    period_name = serializers.CharField(source="assignment.period.name", read_only=True)

    class Meta:
        model = GradeWork
        fields = (
            "id",
            "assignment_id",
            "subject_name",
            "group_name",
            "period_name",
            "title",
            "work_type",
            "work_date",
            "max_score",
            "weight",
            "updated_at",
        )


class TeacherGradeSerializer(serializers.ModelSerializer):
    student_id_number = serializers.IntegerField(source="student.student_id", read_only=True)
    student_name = serializers.CharField(source="student.user.get_full_name", read_only=True)
    work_title = serializers.CharField(source="work.title", read_only=True)
    work_date = serializers.DateField(source="work.work_date", read_only=True)
    subject_name = serializers.CharField(source="work.assignment.subject.name", read_only=True)
    group_name = serializers.CharField(source="work.assignment.group.name", read_only=True)

    class Meta:
        model = Grade
        fields = (
            "id",
            "student",
            "student_id_number",
            "student_name",
            "work",
            "work_title",
            "work_date",
            "subject_name",
            "group_name",
            "value",
            "comment",
            "updated_at",
        )


class TeacherClassSessionSerializer(serializers.ModelSerializer):
    assignment_id = serializers.IntegerField(source="assignment.id", read_only=True)
    subject_name = serializers.CharField(source="assignment.subject.name", read_only=True)
    group_name = serializers.CharField(source="assignment.group.name", read_only=True)
    period_name = serializers.CharField(source="assignment.period.name", read_only=True)

    class Meta:
        model = ClassSession
        fields = ("id", "assignment_id", "subject_name", "group_name", "period_name", "session_date", "topic", "updated_at")


class TeacherAttendanceSerializer(serializers.ModelSerializer):
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
            "student",
            "student_id_number",
            "student_name",
            "session",
            "session_topic",
            "session_date",
            "subject_name",
            "group_name",
            "status",
            "comment",
            "updated_at",
        )
