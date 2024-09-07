from typing import Type, Tuple, List

from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django.db.models import QuerySet, OuterRef

from userportal.models import *


AuthUserType = Type[get_user_model()]


class EnrollmentRepository:
    """Repository for Enrollment model."""

    @staticmethod
    def fetch(student: StudentProfile) -> Tuple[List, List, List]:
        """
        Fetch a student's enrollments and groups them by their term status
        into upcoming, current, and past categories.
        """
        enrollments = Enrollment.objects.filter(student=student).select_related(
            "offering", "offering__course", "offering__term"
        )

        upcoming, current, past = [], [], []
        for enrollment in enrollments:
            term_status = enrollment.offering.term.status
            if term_status == AcademicTerm.TermStatus.NOT_STARTED:
                upcoming.append(enrollment)
            elif term_status == AcademicTerm.TermStatus.IN_PROGRESS:
                current.append(enrollment)
            else:
                past.append(enrollment)

        return upcoming, current, past

    @staticmethod
    def is_enrolled(student_profile: StudentProfile, offering: CourseOffering) -> bool:
        """Check if the student is enrolled in the given course offering."""
        return Enrollment.objects.filter(
            student=student_profile, offering=offering
        ).exists()

    @staticmethod
    def has_finished_course(student_profile: StudentProfile, course: Course) -> bool:
        """Check if the student has finished the given course before."""
        current_time = now()
        return Enrollment.objects.filter(
            student=student_profile,
            offering__course=course,
            offering__term__end_datetime__lt=current_time,
        ).exists()

    @staticmethod
    def fetch_with_student(offering_id: int) -> QuerySet[Enrollment]:
        """Get all enrollments for the given course offering, including related student data."""
        return (
            Enrollment.objects.filter(offering_id=offering_id)
            .select_related("student")
            .order_by("-enrolled_at")
        )

    @staticmethod
    def fetch_latest_grades_subquery(course_id) -> QuerySet[Enrollment]:
        """Get a subquery for the latest grade of a student enrolled in the given course."""
        return (
            Enrollment.objects.filter(
                student=OuterRef("student"),
                offering__course_id=course_id,
                offering__term__end_datetime__lt=now(),
            )
            .order_by("-offering__term__end_datetime")
            .values("grade")[:1]
        )
