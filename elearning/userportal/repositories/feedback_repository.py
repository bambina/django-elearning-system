from userportal.models import *
from django.db.models import OuterRef, Subquery, Case, When, Value
from django.utils.timezone import now
from userportal.repositories import EnrollmentRepository


class FeedbackRepository:
    @staticmethod
    def get_or_none(student, course):
        try:
            feedback = Feedback.objects.get(student=student, course=course)
        except Feedback.DoesNotExist:
            feedback = None
        return feedback

    @staticmethod
    def create(form_data, course, student) -> Feedback:
        feedback = Feedback(**form_data)
        feedback.course = course
        feedback.student = student
        feedback.save()
        return feedback

    @staticmethod
    def get_with_student_grade(course_id):
        latest_grade = EnrollmentRepository.get_latest_grades_subquery(course_id)

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
