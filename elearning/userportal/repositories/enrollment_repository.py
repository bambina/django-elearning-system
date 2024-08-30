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

            for e in enrollments:
                status = e.offering.term.status
                if status == AcademicTerm.TermStatus.NOT_STARTED:
                    upcoming_enrollments.append(e)
                elif status == AcademicTerm.TermStatus.IN_PROGRESS:
                    current_enrollments.append(e)
                else:
                    past_enrollments.append(e)

        return upcoming_enrollments, current_enrollments, past_enrollments
