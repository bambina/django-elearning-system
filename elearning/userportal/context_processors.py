from .models import Notification


def unread_notifications(request):
    # print("unread_notifications is called")
    # print(request.context)
    if not request.user.is_authenticated:
        return {}

    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return {"unread_notifications": count}
