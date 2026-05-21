from rest_framework.permissions import BasePermission


class IsSystemAdmin(BasePermission):
    message = "Доступ разрешен только администратору."

    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(user and user.is_authenticated and user.is_system_admin)


class IsTeacher(BasePermission):
    message = "Доступ разрешен только преподавателю."

    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(user and user.is_authenticated and user.is_teacher)


class IsStudent(BasePermission):
    message = "Доступ разрешен только студенту."

    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(user and user.is_authenticated and user.is_student)
