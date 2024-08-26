from celery import shared_task
from .models import *
from django.urls import reverse


@shared_task
def notify_students_of_live_qa_start(course_id):
    """
    A task to notify students when a live Q&A session starts.
    """
    course = Course.objects.get(id=course_id)
    message = LIVE_QA_START_NOTIFICATION_MSG.format(course_title=course.title)
    link_path = reverse("qa-session", args=[course.id])
    send_notifications_to_currently_enrolled_students(
        course, message, link_path, LIVE_QA_START_NOTIFICATION_LINK_TEXT
    )


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


def send_notifications_to_currently_enrolled_students(
    course, message, link_path, link_text
):
    """
    Sends notifications to students currently enrolled in a course.
    """
    course_offering = CourseOffering.objects.filter(
        course=course, term=AcademicTerm.current()
    ).first()

    if course_offering:
        users = PortalUser.objects.filter(
            student_profile__enrollments__offering=course_offering
        )
    else:
        users = PortalUser.objects.none()
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
