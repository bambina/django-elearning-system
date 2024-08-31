from typing import Union

from django.db.models import QuerySet
from django.db.models import Subquery, Case, When, Value

from userportal.models import *
from userportal.repositories import EnrollmentRepository


class FeedbackRepository:
    """Repository for Feedback model."""

    @staticmethod
    def fetch(student: StudentProfile, course: Course) -> Union[Feedback, None]:
        """Fetches feedback for a given student and course."""
        return Feedback.objects.filter(student=student, course=course).first()

    @staticmethod
    def create(form_data, course, student) -> Feedback:
        """Create a feedback with given form data, course, and student."""
        feedback = Feedback(**form_data)
        feedback.course = course
        feedback.student = student
        feedback.save()
        return feedback

    @staticmethod
    def fetch_with_student_grade(course_id: int) -> QuerySet[Feedback]:
        """Fetch feedback with student grade for a given course."""
        latest_grade = EnrollmentRepository.fetch_latest_grades_subquery(course_id)

        return (
            Feedback.objects.filter(course_id=course_id)
            .annotate(
                grade=Subquery(latest_grade),
                grade_display=Case(
                    When(grade=Enrollment.Grade.PASS, then=Value("Pass")),
                    When(grade=Enrollment.Grade.FAIL, then=Value("Fail")),
                    default=Value("Not Graded"),
                ),
            )
            .select_related("student")
            .order_by("-updated_at")
        )
