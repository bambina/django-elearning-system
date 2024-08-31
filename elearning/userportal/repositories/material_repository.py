from django.db.models.query import QuerySet
from userportal.models import *


class MaterialRepository:
    """Repository for Material model."""

    @staticmethod
    def create(form_data: dict, course: Course) -> Material:
        """Create a material with given form data and course."""
        material = Material(**form_data)
        material.course = course
        material.save()
        return material

    @staticmethod
    def fetch(course: Course) -> QuerySet[Material]:
        """Fetch all materials for the given course."""
        return Material.objects.filter(course=course).only(
            "id", "title", "description", "uploaded_at", "file"
        )
