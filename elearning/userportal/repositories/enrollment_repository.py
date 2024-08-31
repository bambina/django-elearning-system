from typing import Type, Tuple, List
from django.contrib.auth import get_user_model
from userportal.models import *
from django.db.models import QuerySet, OuterRef
from django.utils.timezone import now

User = get_user_model()
AuthUserType = Type[get_user_model()]


class EnrollmentRepository:
    @staticmethod
    def get(student: StudentProfile) -> Tuple[List, List, List]:
        """Get the student's enrollments grouped by term status."""
        upcoming_enrollments = []
        current_enrollments = []
        past_enrollments = []

        enrollments = Enrollment.objects.filter(student=student).select_related(
            "offering", "offering__course", "offering__term"
        )

        for e in enrollments:
            status = e.offering.term.status
            if status == AcademicTerm.TermStatus.NOT_STARTED:
                upcoming_enrollments.append(e)
            elif status == AcademicTerm.TermStatus.IN_PROGRESS:
                current_enrollments.append(e)
            else:
                past_enrollments.append(e)

        return upcoming_enrollments, current_enrollments, past_enrollments

    @staticmethod
    def is_enrolled(student_profile: StudentProfile, offering: CourseOffering) -> bool:
        """Check if the student is enrolled in the given course offering."""
        return Enrollment.objects.filter(
            student=student_profile, offering=offering
        ).exists()

    @staticmethod
    def get_with_student(offering_id: int) -> QuerySet[Enrollment]:
        """Get all enrollments for the given course offering, including related student data."""
        return (
            Enrollment.objects.filter(offering_id=offering_id)
            .select_related("student")
            .order_by("-enrolled_at")
        )

    @staticmethod
    def get_latest_grades_subquery(course_id):
        return (
            Enrollment.objects.filter(
                student=OuterRef("student"),
                offering__course_id=course_id,
                offering__term__end_datetime__lt=now(),
            )
            .order_by("-offering__term__end_datetime")
            .values("grade")[:1]
        )
