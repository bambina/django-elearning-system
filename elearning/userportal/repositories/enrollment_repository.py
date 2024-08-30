from typing import Type, Tuple, List
from django.contrib.auth import get_user_model
from userportal.models import *


User = get_user_model()
AuthUserType = Type[get_user_model()]


class EnrollmentRepository:
    @staticmethod
    def fetch_enrollments_for_student(user: AuthUserType) -> Tuple[List, List, List]:
        upcoming_enrollments = []
        current_enrollments = []
        past_enrollments = []

        if user.is_student():
            enrollments = Enrollment.objects.filter(
                student=user.student_profile
            ).select_related("offering", "offering__course", "offering__term")

            for enrollment in enrollments:
                if (
                    enrollment.offering.term.status
                    == AcademicTerm.TermStatus.NOT_STARTED
                ):
                    upcoming_enrollments.append(enrollment)
                elif (
                    enrollment.offering.term.status
                    == AcademicTerm.TermStatus.IN_PROGRESS
                ):
                    current_enrollments.append(enrollment)
                else:
                    past_enrollments.append(enrollment)

        return upcoming_enrollments, current_enrollments, past_enrollments
