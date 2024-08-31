from django.db.models import Q
from django.db.models.query import QuerySet

from userportal.models import *


class CourseRepository:
    """Repository for Course model."""

    @staticmethod
    def fetch_filtered_by(keywords: dict = None) -> QuerySet[Course]:
        """Fetch courses that match the given keywords."""
        queryset = Course.objects.select_related("teacher__user").only(
            "id",
            "title",
            "description",
            "teacher__user__title",
            "teacher__user__first_name",
            "teacher__user__last_name",
        )
        if keywords:
            query_words = keywords.split()
            q_objects = Q()
            for word in query_words:
                q_objects |= (
                    Q(title__icontains=word)
                    | Q(description__icontains=word)
                    | Q(teacher__user__first_name__icontains=word)
                    | Q(teacher__user__last_name__icontains=word)
                )
            queryset = queryset.filter(q_objects)
        return queryset

    @staticmethod
    def create_course(form_data: dict, teacher: TeacherProfile) -> Course:
        """Create a course with given form data and teacher."""
        course = Course(**form_data)
        course.teacher = teacher
        course.save()
        return course
