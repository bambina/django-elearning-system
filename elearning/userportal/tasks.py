from celery import shared_task
from .models import *


@shared_task
def create_notifications_for_enrolled_students(
    course_id, message, link_path, link_text
):
    """
    A task to create notifications for students enrolled in a course.
    """
    students = StudentProfile.objects.filter(
        courses__offering__course_id=course_id,
        courses__offering__term=AcademicTerm.current(),
    ).only("user")
    users = [student.user for student in students]
    send_notifications(users, message, link_path, link_text)


def send_notifications(
    users: list[PortalUser], message: str, link_path: str = None, link_text: str = None
):
    """
    Sends notifications to users
    """
    notifications = [
        Notification(
            user=user, message=message, link_path=link_path, link_text=link_text
        )
        for user in users
    ]
    Notification.objects.bulk_create(notifications)


@shared_task
def mark_notifications_as_read(notification_ids):
    """
    A task to mark a notification as read.
    """
    Notification.objects.filter(id__in=notification_ids).update(is_read=True)
