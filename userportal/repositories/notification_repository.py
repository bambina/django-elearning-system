from typing import Type
from django.db.models import QuerySet
from userportal.models import Notification
from django.contrib.auth import get_user_model

AuthUserType = Type[get_user_model()]


class NotificationRepository:
    """Repository for Notification model."""

    @staticmethod
    def fetch(user: AuthUserType) -> QuerySet[Notification]:
        """Fetch notifications for the given user."""
        return Notification.objects.filter(user=user).order_by("-created_at")
