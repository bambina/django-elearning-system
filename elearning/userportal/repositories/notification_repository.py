from userportal.models import Notification


class NotificationRepository:
    @staticmethod
    def fetch_notifications_for(user):
        return Notification.objects.filter(user=user).order_by("-created_at")
