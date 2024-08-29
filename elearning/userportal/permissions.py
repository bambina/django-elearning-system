from userportal.models import *
from django.contrib.auth import get_user_model
from typing import Type

# Get the auth user model type
AuthUserType = Type[get_user_model()]


class PermissionChecker:
    @staticmethod
    def is_admin(user: AuthUserType) -> bool:
        return user.is_staff or user.is_superuser

    @staticmethod
    def is_teacher_or_admin(user: AuthUserType) -> bool:
        is_authenticated = user.is_authenticated
        is_teacher = user.groups.filter(name="teacher").exists()
        is_manager = PermissionChecker.is_admin(user)
        return is_authenticated and (is_teacher or is_manager)

    @staticmethod
    def is_taking_course(profile: StudentProfile, course: Course) -> bool:
        offering = CourseOffering.objects.filter(
            course=course,
            term=AcademicTerm.current(),
        ).first()
        if not offering:
            return False
        return Enrollment.objects.filter(student=profile, offering=offering).exists()

    @staticmethod
    def is_teaching_course(profile: TeacherProfile, course: Course) -> bool:
        return profile == course.teacher

    @staticmethod
    def is_active_in_course(user: AuthUserType, course: Course) -> bool:
        if user.is_teacher():
            return PermissionChecker.is_teaching_course(user.teacher_profile, course)
        if user.is_student():
            return PermissionChecker.is_taking_course(user.student_profile, course)
        return False
