from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.users.models import UserRole
from apps.users.serializers import UserReadSerializer

from .models import AcademicGroup, AcademicPeriod, StudentProfile, Subject, TeacherProfile, TeachingAssignment


User = get_user_model()


class AcademicGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicGroup
        fields = ("id", "name", "enrollment_year", "is_active")


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ("id", "name", "code", "description", "is_active")


class AcademicPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicPeriod
        fields = ("id", "name", "starts_at", "ends_at", "is_active")


class StudentProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role=UserRole.STUDENT))
    group = serializers.PrimaryKeyRelatedField(queryset=AcademicGroup.objects.all())
    user_details = UserReadSerializer(source="user", read_only=True)
    group_name = serializers.CharField(source="group.name", read_only=True)

    class Meta:
        model = StudentProfile
        fields = ("id", "user", "user_details", "student_id", "group", "group_name", "enrollment_date")

    def validate_user(self, user):
        if user.role != UserRole.STUDENT:
            raise serializers.ValidationError("Профиль студента можно создать только для пользователя с ролью студента.")
        return user


class TeacherProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role=UserRole.TEACHER))
    user_details = UserReadSerializer(source="user", read_only=True)

    class Meta:
        model = TeacherProfile
        fields = ("id", "user", "user_details", "personnel_number", "position")

    def validate_user(self, user):
        if user.role != UserRole.TEACHER:
            raise serializers.ValidationError("Профиль преподавателя можно создать только для пользователя с ролью преподавателя.")
        return user


class TeachingAssignmentSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(queryset=TeacherProfile.objects.select_related("user").all())
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all())
    group = serializers.PrimaryKeyRelatedField(queryset=AcademicGroup.objects.all())
    period = serializers.PrimaryKeyRelatedField(queryset=AcademicPeriod.objects.all())
    teacher_name = serializers.CharField(source="teacher.user.get_full_name", read_only=True)
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    group_name = serializers.CharField(source="group.name", read_only=True)
    period_name = serializers.CharField(source="period.name", read_only=True)

    class Meta:
        model = TeachingAssignment
        fields = (
            "id",
            "teacher",
            "teacher_name",
            "subject",
            "subject_name",
            "group",
            "group_name",
            "period",
            "period_name",
        )
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=TeachingAssignment.objects.all(),
                fields=("teacher", "subject", "group", "period"),
                message="Такое назначение преподавателя уже существует.",
            )
        ]
