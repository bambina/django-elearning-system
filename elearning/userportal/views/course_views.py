from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.views.generic import ListView, DetailView
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.conf import settings
from django.http import FileResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from userportal.consumers import *
from userportal.models import *
from userportal.forms import *
from userportal.tasks import *
from userportal.permissions import PermissionChecker
from userportal.repositories import *
from userportal.views.mixins import QueryParamsMixin
from django.contrib.auth import get_user_model
from typing import Type
from userportal.constants import *
from django.db import transaction

AuthUserType = Type[get_user_model()]


class CourseListView(QueryParamsMixin, ListView):
    model = Course
    paginate_by = settings.PAGINATION_PAGE_SIZE
    template_name = "userportal/course_list.html"
    context_object_name = "courses"

    def get_queryset(self):
        keywords = self.request.GET.get("keywords")
        return CourseRepository.fetch_filtered_by(keywords)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = CourseSearchForm(self.request.GET or None)
        return context


class CourseDetailView(DetailView):
    model = Course
    template_name = "userportal/course_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        course = self.object
        # Return early for anonymous users
        if user.is_anonymous:
            return context

        # Add course offering data
        context.update(self.get_course_offerings_context(course))
        # Add QA session data
        context.update(self.get_qa_session_context(course))
        # Add request user's data
        if user.is_student():
            context.update(self.get_student_context(user.student_profile, context))
        elif user.is_teacher():
            context["is_instructor"] = user.teacher_profile == course.teacher

        return context

    @staticmethod
    def get_course_offerings_context(course: Course) -> dict:
        """Get the current and next course offerings for the given course."""
        return {
            "next_offering": CourseOfferingRepository.fetch_next(course),
            "current_offering": CourseOfferingRepository.fetch_current(course),
        }

    @staticmethod
    def get_student_context(profile: StudentProfile, context: dict) -> dict:
        """Get the student's enrollment status for the current and next course offerings."""
        return {
            "is_taking": EnrollmentRepository.is_enrolled(
                profile, context["current_offering"]
            ),
            "is_registered": EnrollmentRepository.is_enrolled(
                profile, context["next_offering"]
            ),
        }

    @staticmethod
    def get_qa_session_context(course: Course) -> dict:
        """Get the active or ended QA session for the course."""
        qa_session = QASessionRepository.fetch(course)
        return {
            "qa_session": qa_session,
            "show_start_session_button": not qa_session or qa_session.is_ended(),
        }


@login_required(login_url="login")
def create_course(request):
    if not request.user.is_teacher():
        messages.error(request, ERR_ONLY_TEACHERS_CAN_CREATE_COURSES)
        return redirect("course-list")

    teacher = get_object_or_404(TeacherProfile, user=request.user)
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            try:
                course = CourseRepository.create(form.cleaned_data, teacher)
                messages.success(request, CREATED_SUCCESS_MSG.format(entity="course"))
                return redirect("course-detail", pk=course.pk)
            except Exception:
                form.add_error(None, ERR_UNEXPECTED_MSG)
    else:
        form = CourseForm()
    return render(request, "userportal/course_create.html", {"form": form})


@login_required(login_url="login")
def create_material(request, course_id):
    if not request.user.is_teacher():
        messages.error(request, ERR_ONLY_TEACHERS_CAN_CREATE_MATERIALS)
        return redirect("course-list")

    course = get_object_or_404(Course, pk=course_id)
    if request.method == "POST":
        form = MaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = MaterialRepository.create(
                form.cleaned_data, course, request.FILES
            )
            # Asynchronously send notifications to students enrolled in the course
            notify_students_of_material_creation.delay(course.id, material.id)
            messages.success(request, CREATED_SUCCESS_MSG.format(entity="material"))
            return redirect("course-detail", pk=course.id)
    else:
        form = MaterialForm()
    return render(
        request, "userportal/material_create.html", {"course": course, "form": form}
    )


class MaterialListView(ListView):
    model = Material
    paginate_by = settings.PAGINATION_PAGE_SIZE
    template_name = "userportal/material_list.html"
    context_object_name = "materials"
    login_url = "login"

    def get_queryset(self):
        course_id = self.kwargs.get("course_id")
        course = get_object_or_404(Course, pk=course_id)
        return MaterialRepository.fetch(course)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course"] = get_object_or_404(Course, pk=self.kwargs.get("course_id"))
        return context


def download_material(request, course_id, material_id):
    course = get_object_or_404(Course, pk=course_id)
    material = get_object_or_404(Material, pk=material_id)

    if not material.file:
        messages.error(request, ERR_DOES_NOT_EXIST.format(entity="file"))
        return redirect("material-list", course_id=course.id)

    response = FileResponse(material.file, as_attachment=True)
    response["Content-Disposition"] = (
        f'attachment; filename="{material.original_filename}"'
    )
    return response


@require_http_methods(["POST"])
def start_qa_session(request, course_id):
    # Only teachers can start a QA session
    if not PermissionChecker.is_teacher_or_admin(request.user):
        messages.error(request, ERR_ONLY_AUTHORIZED_CAN_MANAGE_QA_SESSIONS)
        return redirect("course-detail", pk=course_id)

    course = get_object_or_404(Course, pk=course_id)
    qa_session, created = QASession.objects.get_or_create(course=course)

    # Check the last session status
    if not created:
        if qa_session.is_active():
            # Show a message and redirect to the QA session page if already started
            messages.warning(request, ACTIVE_QA_SESSION_EXISTS)
            return redirect("qa-session", course_id=course.id)
        elif qa_session.is_ended():
            # Delete all previous questions asynchronously
            delete_qa_questions.delay(qa_session.room_name)

    # Update the room name
    qa_session = QASessionRepository.update_room_name(qa_session)
    # Notify students enrolled in the course
    notify_students_of_live_qa_start.delay(course.id)
    # Prepare context for the template
    context = {
        "course": course,
        "qa_session": qa_session,
        "is_instructor": request.user.teacher_profile == course.teacher,
    }
    return render(request, "userportal/qa_session.html", context=context)


def qa_session(request, course_id):
    user = request.user
    course = get_object_or_404(Course, pk=course_id)
    qa_session = get_object_or_404(QASession, course=course)
    # Setup the context for the QA session page
    context = {
        "course": course,
        "qa_session": qa_session,
        "is_instructor": user.is_teacher() and user.teacher_profile == course.teacher,
    }
    if qa_session.is_ended():
        # If the QA session has ended, fetch the questions as WebSocket is not available
        context["questions"] = QAQuestion.objects.filter(room_name=qa_session.room_name)
    return render(request, "userportal/qa_session.html", context=context)


@require_http_methods(["POST"])
def end_qa_session(request, course_id):
    if not PermissionChecker.is_teacher_or_admin(request.user):
        messages.error(request, ERR_ONLY_AUTHORIZED_CAN_MANAGE_QA_SESSIONS)
        return redirect("qa-session", course_id=course_id)

    course = get_object_or_404(Course, pk=course_id)

    try:
        with transaction.atomic():
            _, close_comment = _end_session_and_create_comment(course)
    except Exception as e:
        messages.error(request, ERR_FAILED_TO_END_SESSION.format(exception=e))
        return redirect("qa-session", course_id=course.id)

    _send_close_message(close_comment)

    messages.success(request, QA_SESSION_END_SUCCESS_MSG)
    return redirect("course-detail", pk=course.id)


def _end_session_and_create_comment(course: Course) -> tuple[QASession, QAQuestion]:
    """
    End the QA session and create a close comment in an atomic operation.
    """
    qa_session = QASessionRepository.end(course)
    close_comment = QAQuestionRepository.create_and_save_close_comment(qa_session)
    return qa_session, close_comment


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
