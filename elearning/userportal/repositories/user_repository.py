from typing import Type
from django.db.models import Q
from django.db.models.query import QuerySet
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from userportal.models import StudentProfile

AuthUser = get_user_model()
AuthUserType = Type[get_user_model()]


class UserRepository:
    """Repository for User model."""

    @staticmethod
    def fetch_filtered_by(keywords=None, user_types=None) -> QuerySet[AuthUserType]:
        """Fetch users that match the given keywords and user types."""
        queryset = AuthUser.objects.filter(is_staff=False, is_superuser=False).only(
            "id", "username", "user_type", "is_active"
        )

        if keywords:
            query_words = keywords.split()
            q_objects = Q()
            for word in query_words:
                q_objects |= (
                    Q(username__icontains=word)
                    | Q(first_name__icontains=word)
                    | Q(last_name__icontains=word)
                    | Q(title__icontains=word)
                )
            queryset = queryset.filter(q_objects)

        if user_types:
            queryset = queryset.filter(user_type__in=user_types)

        return queryset

    @staticmethod
    def toggle_user_active_status(username, activate=True) -> bool:
        """Toggle the active status of the user with the given username."""
        user = get_object_or_404(AuthUser, username=username)
        if activate != user.is_active:
            user.is_active = activate
            user.save()
            return True
        return False

    @staticmethod
    def update_status(student: StudentProfile, status: str) -> StudentProfile:
        """Update the status of the student."""
        student.status = status
        student.save()
        return student
