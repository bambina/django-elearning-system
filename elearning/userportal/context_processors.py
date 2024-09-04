from .models import Notification
from django.http import HttpRequest
from typing import Dict, Any


def unread_notifications(request: HttpRequest) -> Dict[str, Any]:
    """Count of unread notifications for the request user."""
    if not request.user.is_authenticated:
        return {}

    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return {"unread_notifications": count}
