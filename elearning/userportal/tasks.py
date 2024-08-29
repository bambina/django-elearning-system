from celery import shared_task
from .models import *
from django.urls import reverse
from celery.utils.log import get_task_logger
from userportal.repositories.academic_term_repository import AcademicTermRepository

logger = get_task_logger(__name__)


@shared_task
def delete_qa_questions(room_name):
    """
    A task to delete all questions in the the specified Q&A session.
    """
    QAQuestion.objects.filter(room_name=room_name).delete()


@shared_task
def notify_students_of_live_qa_start(course_id):
    """
    A task to notify students when a live Q&A session starts.
    """
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        logger.error(ERR_DOES_NOT_EXIST.format(entity=f"Course with ID {course_id}"))
        return
    message = LIVE_QA_START_NOTIFICATION_MSG.format(course_title=course.title)
    link_path = reverse("qa-session", args=[course.id])
    send_notifications_to_currently_enrolled_students(
        course, message, link_path, LIVE_QA_START_NOTIFICATION_LINK_TEXT
    )


@shared_task
def notify_students_of_material_creation(course_id, material_id):
    """
    A task to notify students when a new material is added to a course.
    """
    try:
        course = Course.objects.get(id=course_id)
        material = Material.objects.get(id=material_id)
    except Course.DoesNotExist:
        logger.error(ERR_DOES_NOT_EXIST.format(entity=f"Course with ID {course_id}"))
        return
    except Material.DoesNotExist:
        logger.error(
            ERR_DOES_NOT_EXIST.format(entity=f"Material with ID {material_id}")
        )
        return
    message = MATERIAL_CREATED_NOTIFICATION_MSG.format(
        material_title=material.title, course_title=course.title
    )
    link_path = reverse("material-list", args=[course.id])
    send_notifications_to_currently_enrolled_students(
        course, message, link_path, MATERIAL_CREATED_NOTIFICATION_LINK_TEXT
    )


@shared_task
def notify_teacher_of_new_enrollment(course_id, offering_id, student_username):
    """
    A task to create a notification for a teacher when a student enrolls in a course.
    """
    try:
        course = Course.objects.select_related("teacher__user").get(id=course_id)
    except Course.DoesNotExist:
        logger.error(ERR_DOES_NOT_EXIST.format(entity=f"Course with ID {course_id}"))
        return
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
        course=course, term=AcademicTermRepository.current()
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
    try:
        Notification.objects.bulk_create(notifications)
    except Exception as e:
        logger.error(ERR_FAILED_TO_SEND_NOTIFICATION.format(exception=str(e)))


@shared_task
def mark_notifications_as_read(notification_ids):
    """
    A task to mark a notification as read.
    """
    Notification.objects.filter(id__in=notification_ids).update(is_read=True)
