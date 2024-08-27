class PermissionChecker:
    @staticmethod
    def is_teacher_or_admin(user):
        is_authenticated = user.is_authenticated
        is_teacher = user.groups.filter(name="teacher").exists()
        is_manager = user.is_staff or user.is_superuser
        return is_authenticated and (is_teacher or is_manager)
