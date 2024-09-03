from userportal.models import *
from django.contrib.auth import get_user_model
from typing import Type, Union
from django.contrib.auth.models import AnonymousUser
from userportal.repositories import *

# Get the auth user model type
AuthUserType = Type[get_user_model()]


class PermissionChecker:
    @staticmethod
    def is_admin(user: AuthUserType) -> bool:
        return user.is_staff or user.is_superuser

    @staticmethod
    def is_teacher_or_admin(user: AuthUserType) -> bool:
        is_authenticated = user.is_authenticated
        is_teacher = user.groups.filter(name=PERMISSION_GROUP_TEACHER).exists()
        is_admin = PermissionChecker.is_admin(user)
        return is_authenticated and (is_teacher or is_admin)

    @staticmethod
    def is_taking_course(profile: StudentProfile, course: Course) -> bool:
        offering = CourseOffering.objects.filter(
            course=course,
            term=AcademicTermRepository.current(),
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

    @staticmethod
    def has_finished_course(
        request_user: Union[AuthUserType, AnonymousUser], course: Course
    ) -> bool:
        # Return False for the anonymous user
        if not request_user.is_authenticated:
            return False
        # Return False if the user is not in the student permission group
        if not request_user.groups.filter(name=PERMISSION_GROUP_STUDENT).exists():
            return False
        # Return True if the user has finished the course before
        return EnrollmentRepository.has_finished_course(
            request_user.student_profile, course
        )

    @staticmethod
    def can_manage_qa_session(
        request_user: Union[AuthUserType, AnonymousUser], course: Course
    ) -> bool:
        # Return False for the anonymous user
        if not request_user.is_authenticated:
            return False
        # Return False if the user is not in the teacher permission group
        if not request_user.groups.filter(name=PERMISSION_GROUP_TEACHER).exists():
            return False
        return PermissionChecker.is_admin or PermissionChecker.is_teaching_course(
            request_user.teacher_profile, course
        )
