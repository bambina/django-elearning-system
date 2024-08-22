from rest_framework import permissions


class IsTeacherGroupOrAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow teachers and admin users to access the view.
    """

    def has_permission(self, request, view):
        is_authenticated = request.user.is_authenticated
        is_teacher = request.user.groups.filter(name="teacher").exists()
        is_manager = request.user.is_staff or request.user.is_superuser
        return is_authenticated and (is_teacher or is_manager)
