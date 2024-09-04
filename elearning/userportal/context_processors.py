from .models import Notification
from django.http import HttpRequest
from typing import Dict, Any


def unread_notifications(request: HttpRequest) -> Dict[str, Any]:
    """
    Django context processor for counting unread notifications.

    This function is designed to be used as a context processor in Django.
    It adds the count of unread notifications for the requested user
    to the template context.
    """
    if not request.user.is_authenticated:
        return {}

    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return {"unread_notifications": count}
