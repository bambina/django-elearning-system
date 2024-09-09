from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from django.db import transaction
from django.contrib import messages
from django.views.generic import DetailView
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from userportal.tasks import *
from userportal.models import *
from userportal.repositories import *
from userportal.permissions import PermissionChecker


@login_required(login_url="login")
@require_http_methods(["POST"])
def start_qa_session(request, course_id):
    """Start a QA session for a course."""

    # Only teachers can start a QA session
    course = get_object_or_404(Course, pk=course_id)
    if not PermissionChecker.can_manage_qa_session(request.user, course):
        messages.error(request, ERR_ONLY_AUTHORIZED_CAN_MANAGE_QA_SESSIONS)
        return redirect("course-detail", pk=course_id)

    try:
        created, already_available, room_name_to_be_deleted = (
            QASessionRepository.get_create_or_reactivate(course=course)
        )
    except Exception:
        messages.error(request, ERR_UNEXPECTED_MSG)
        return redirect("course-detail", pk=course.id)

    if created or room_name_to_be_deleted:
        # Notify students enrolled in the course
        notify_students_of_live_qa_start.delay(course.id)

    if already_available:
        # Show a message if already started
        messages.warning(request, ACTIVE_QA_SESSION_EXISTS)

    if room_name_to_be_deleted:
        # Delete all previous questions asynchronously
        delete_qa_questions.delay(room_name_to_be_deleted)
    return redirect("qa-session", course_id=course.id)


class QASessionView(UserPassesTestMixin, DetailView):
    """View for a QA session."""

    model = QASession
    template_name = "userportal/qa_session.html"
    context_object_name = "qa_session"
    login_url = "login"

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, pk=self.kwargs["course_id"])
        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        is_admin = PermissionChecker.is_admin(self.request.user)
        is_active_in_course = PermissionChecker.is_active_in_course(
            self.request.user, self.course
        )
        return is_admin or is_active_in_course

    def get_object(self):
        return get_object_or_404(QASession, course=self.course)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        course = self.object.course

        context["course"] = course
        context["is_instructor"] = (
            user.is_teacher() and user.teacher_profile == course.teacher
        )

        if self.object.is_ended():
            context["questions"] = QAQuestion.objects.filter(
                room_name=self.object.room_name
            )

        return context


@login_required(login_url="login")
@require_http_methods(["POST"])
def end_qa_session(request, course_id):
    """End a QA session for a course."""
    course = get_object_or_404(Course, pk=course_id)
    if not PermissionChecker.can_manage_qa_session(request.user, course):
        messages.error(request, ERR_ONLY_AUTHORIZED_CAN_MANAGE_QA_SESSIONS)
        return redirect("course-detail", pk=course.id)

    try:
        with transaction.atomic():
            close_comment = _end_session_and_create_comment(course)
    except Exception as e:
        messages.error(request, ERR_FAILED_TO_END_SESSION.format(exception=e))
        return redirect("qa-session", course_id=course.id)

    _send_close_message(close_comment)
    messages.success(request, QA_SESSION_END_SUCCESS_MSG)
    return redirect("course-detail", pk=course.id)


def _end_session_and_create_comment(course: Course) -> QAQuestion:
    """
    End the QA session and create a close comment in an atomic operation.
    """
    qa_session = QASessionRepository.end(course)
    return QAQuestionRepository.create_and_save_close_comment(qa_session)


def _send_close_message(close_comment: QAQuestion) -> None:
    """
    Send a close message to the group via WebSocket.
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"{LIVE_QA_PREFIX}_{close_comment.room_name}",
        {
            "type": MESSAGE_TYPE_CLOSE,
            "message": close_comment.text,
            "sender": close_comment.sender,
            "timestamp": close_comment.timestamp.isoformat(),
        },
    )
