from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsJournalParticipant(BasePermission):
    message = "Нет прав для работы с этим журналом."

    def has_permission(self, request, view) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_system_admin:
            return True
        if request.method in SAFE_METHODS:
            return user.is_teacher or user.is_student
        return user.is_teacher

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        if user.is_system_admin:
            return True

        assignment = getattr(obj, "assignment", None)
        if assignment is None and hasattr(obj, "work"):
            assignment = obj.work.assignment
        if assignment is None and hasattr(obj, "session"):
            assignment = obj.session.assignment

        if user.is_teacher:
            return assignment.teacher.user_id == user.id

        if request.method in SAFE_METHODS and user.is_student:
            student_profile = getattr(user, "student_profile", None)
            if student_profile is None:
                return False
            if hasattr(obj, "student_id"):
                return obj.student_id == student_profile.id
            return assignment.group_id == student_profile.group_id

        return False
