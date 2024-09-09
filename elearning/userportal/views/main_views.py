from django.conf import settings
from django.shortcuts import render
from django.contrib import messages
from django.views.generic import ListView
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required

from userportal.models import *
from userportal.forms import *
from userportal.repositories import *
from userportal.tasks import mark_notifications_as_read


def top(request: HttpRequest) -> HttpResponse:
    """Top page view."""
    return render(request, "userportal/top.html")


@login_required(login_url="login")
def home(request: HttpRequest) -> HttpResponse:
    """Home page view."""
    context = {}
    user = request.user

    if user.is_student():
        context.update(_handle_student_view(request, user.student_profile))
    elif user.is_teacher():
        context.update(_handle_teacher_view(user.teacher_profile))

    return render(request, "userportal/home.html", context)


def _handle_student_view(request: HttpRequest, student: StudentProfile) -> dict:
    """Prepare the context for the student."""
    form = StatusForm(request.POST or None, initial={"status": student.status})

    if request.method == "POST" and form.is_valid():
        try:
            status = form.cleaned_data["status"]
            UserRepository.update_status(student, status)
            messages.success(request, UPDATE_STATUS_SUCCESS_MSG)
        except Exception:
            form.add_error(None, ERR_UNEXPECTED_MSG)
    context = {"status_form": form}
    enrollments = EnrollmentRepository.fetch(student)
    (
        context["upcoming_enrollments"],
        context["current_enrollments"],
        context["past_enrollments"],
    ) = enrollments
    return context


def _handle_teacher_view(teacher: TeacherProfile) -> dict:
    """Prepare the context for the teacher."""
    return {
        "offered_courses": teacher.courses.all(),
    }


class NotificationListView(ListView):
    """List of notifications for the current user."""

    model = Notification
    paginate_by = settings.PAGINATION_PAGE_SIZE
    template_name = "userportal/notification_list.html"
    context_object_name = "notifications"
    login_url = "login"

    def get_queryset(self):
        return NotificationRepository.fetch(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Search for new notifications, and mark them as read asynchronously
        page_obj = context.get("page_obj")
        if page_obj:
            unread_notification_ids = [
                notification.id
                for notification in page_obj.object_list
                if not notification.is_read
            ]
            if unread_notification_ids:
                # Mark the notifications as read asynchronously
                mark_notifications_as_read.delay(unread_notification_ids)
        return context
