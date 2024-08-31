from userportal.models import *


class MaterialRepository:
    @staticmethod
    def create_material(form_data, course):
        """Create a material with given form data and course."""
        material = Material(**form_data)
        material.course = course
        material.save()
        return material

    @staticmethod
    def get_materials_for(course: Course):
        """Get all materials for the given course."""
        return Material.objects.filter(course=course).only(
            "id", "title", "description", "uploaded_at", "file"
        )
