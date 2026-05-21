from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnlyAuthenticated(BasePermission):
    message = "Изменение учебных справочников доступно только администратору."

    def has_permission(self, request, view) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return user.is_system_admin
