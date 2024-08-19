from celery import shared_task
from .models import *
from django.urls import reverse


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


@shared_task
def notify_teacher_of_new_enrollment(course_id, offering_id, student_username):
    """
    A task to create a notification for a teacher when a student enrolls in a course.
    """
    course = Course.objects.select_related("teacher__user").get(id=course_id)
    teacher = course.teacher.user
    message = STUDENT_ENROLLED_NOTIFICATION_MSG.format(
        username=student_username, course_title=course.title
    )
    link_path = reverse("enrolled-student-list", args=[course_id, offering_id])
    send_notifications(
        [teacher], message, link_path, STUDENT_ENROLLED_NOTIFICATION_LINK_TEXT
    )


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
