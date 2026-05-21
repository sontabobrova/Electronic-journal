from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers

from apps.audit.models import AuditAction
from apps.audit.services import log_audit_event

from .models import UserRole


User = get_user_model()


class UserReadSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="get_full_name", read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "phone",
            "email",
            "role",
            "access_expires_at",
            "is_active",
            "last_login",
            "date_joined",
        )
        read_only_fields = ("id", "last_login", "date_joined")


class UserWriteSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, min_length=6)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "password",
            "first_name",
            "last_name",
            "phone",
            "email",
            "role",
            "access_expires_at",
            "is_active",
        )
        read_only_fields = ("id",)

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value

    def validate_role(self, value: str) -> str:
        if value not in UserRole.values:
            raise serializers.ValidationError("Неизвестная роль пользователя.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        if not password:
            raise serializers.ValidationError({"password": "Пароль обязателен при создании пользователя."})

        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
            instance.reset_login_failures()
        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    default_error_messages = {
        "invalid_credentials": "Неверный логин или пароль.",
        "inactive": "Учетная запись отключена.",
        "expired": "Срок доступа к системе истек.",
        "locked": "Учетная запись временно заблокирована. Повторите попытку позже.",
    }

    def validate(self, attrs):
        request = self.context["request"]
        username = attrs["username"]
        password = attrs["password"]

        user = User.objects.filter(username=username).first()
        if user and user.is_login_locked():
            log_audit_event(
                action=AuditAction.LOGIN_FAILED,
                actor=user,
                request=request,
                obj=user,
                metadata={"reason": "locked", "username": username},
            )
            raise serializers.ValidationError({"detail": self.error_messages["locked"]})

        if user and not user.is_active:
            log_audit_event(
                action=AuditAction.LOGIN_FAILED,
                actor=user,
                request=request,
                obj=user,
                metadata={"reason": "inactive", "username": username},
            )
            raise serializers.ValidationError({"detail": self.error_messages["inactive"]})

        if user and not user.has_active_access():
            log_audit_event(
                action=AuditAction.LOGIN_FAILED,
                actor=user,
                request=request,
                obj=user,
                metadata={"reason": "expired", "username": username},
            )
            raise serializers.ValidationError({"detail": self.error_messages["expired"]})

        authenticated_user = authenticate(request=request, username=username, password=password)
        if authenticated_user is None:
            if user:
                user.register_failed_login()
            log_audit_event(
                action=AuditAction.LOGIN_FAILED,
                actor=user,
                request=request,
                obj=user,
                object_type="User",
                object_id=str(user.id) if user else "",
                object_repr=username,
                metadata={"reason": "invalid_credentials", "username": username},
            )
            raise serializers.ValidationError({"detail": self.error_messages["invalid_credentials"]})

        authenticated_user.reset_login_failures()
        login(request, authenticated_user)
        log_audit_event(action=AuditAction.LOGIN_SUCCESS, actor=authenticated_user, request=request, obj=authenticated_user)
        attrs["user"] = authenticated_user
        return attrs


class PasswordResetByAdminSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, min_length=6)

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value

    def save(self, **kwargs):
        user = self.context["user"]
        user.set_password(self.validated_data["password"])
        user.reset_login_failures()
        user.locked_until = None
        user.failed_login_attempts = 0
        user.save(update_fields=["password", "failed_login_attempts", "locked_until"])
        return user


class CurrentUserSerializer(UserReadSerializer):
    permissions = serializers.SerializerMethodField()

    class Meta(UserReadSerializer.Meta):
        fields = UserReadSerializer.Meta.fields + ("permissions",)

    def get_permissions(self, user) -> dict[str, bool]:
        return {
            "is_student": user.is_student,
            "is_teacher": user.is_teacher,
            "is_admin": user.is_system_admin,
            "has_active_access": user.has_active_access(),
            "is_locked": user.locked_until is not None and user.locked_until > timezone.now(),
        }
