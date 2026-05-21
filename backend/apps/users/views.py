from django.contrib.auth import logout
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.models import AuditAction
from apps.audit.services import log_audit_event

from .models import User
from .permissions import IsSystemAdmin
from .serializers import (
    CurrentUserSerializer,
    LoginSerializer,
    PasswordResetByAdminSerializer,
    UserReadSerializer,
    UserWriteSerializer,
)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        return Response(CurrentUserSerializer(serializer.validated_data["user"]).data)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        log_audit_event(action=AuditAction.LOGOUT, actor=request.user, request=request, obj=request.user)
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(CurrentUserSerializer(request.user).data)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.order_by("last_name", "first_name", "username")
    permission_classes = [IsSystemAdmin]

    def get_serializer_class(self):
        if self.action in {"create", "update", "partial_update"}:
            return UserWriteSerializer
        return UserReadSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        log_audit_event(
            action=AuditAction.USER_CREATED,
            actor=self.request.user,
            request=self.request,
            obj=user,
            metadata={"role": user.role},
        )

    def perform_update(self, serializer):
        user = serializer.save()
        log_audit_event(
            action=AuditAction.USER_UPDATED,
            actor=self.request.user,
            request=self.request,
            obj=user,
            metadata={"role": user.role},
        )

    @action(detail=True, methods=["post"], url_path="reset-password")
    def reset_password(self, request, pk=None):
        user = self.get_object()
        serializer = PasswordResetByAdminSerializer(data=request.data, context={"user": user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        log_audit_event(action=AuditAction.PASSWORD_RESET, actor=request.user, request=request, obj=user)
        return Response(UserReadSerializer(user).data)
