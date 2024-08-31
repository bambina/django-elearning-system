from userportal.models import *
from userportal.repositories.academic_term_repository import *
from typing import Union
from django.db.models import QuerySet


class CourseOfferingRepository:
    @staticmethod
    def get_current(course: Course) -> Union[CourseOffering, None]:
        """Get the current course offering for the given course."""
        current_term = AcademicTermRepository.current()
        if current_term:
            return CourseOffering.objects.filter(
                course=course, term=current_term
            ).first()
        return None

    @staticmethod
    def get_next(course: Course) -> Union[CourseOffering, None]:
        """Get the next course offering for the given course."""
        next_term = AcademicTermRepository.next()
        if next_term:
            return CourseOffering.objects.filter(course=course, term=next_term).first()
        return None

    @staticmethod
    def get_with_academic_terms(course_id: int) -> QuerySet[CourseOffering]:
        """
        Retrieve all course offerings for the given course, including related academic terms.
        """
        return (
            CourseOffering.objects.filter(course_id=course_id)
            .select_related("term")
            .order_by("-term__start_datetime")
        )

    @staticmethod
    def create(form_data: dict, course: Course) -> CourseOffering:
        """Create a new course offering."""
        offering = CourseOffering(**form_data)
        offering.course = course
        offering.save()
        return offering
