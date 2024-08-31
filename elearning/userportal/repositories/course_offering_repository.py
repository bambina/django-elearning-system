from userportal.models import *
from userportal.repositories.academic_term_repository import *
from typing import Union


class CourseOfferingRepository:
    @staticmethod
    def get_current_course_offering(course: Course) -> Union[CourseOffering, None]:
        """Get the current course offering for the given course."""
        current_term = AcademicTermRepository.current()
        if current_term:
            return CourseOffering.objects.filter(
                course=course, term=current_term
            ).first()
        return None

    @staticmethod
    def get_next_course_offering(course: Course) -> Union[CourseOffering, None]:
        """Get the next course offering for the given course."""
        next_term = AcademicTermRepository.next()
        if next_term:
            return CourseOffering.objects.filter(course=course, term=next_term).first()
        return None
