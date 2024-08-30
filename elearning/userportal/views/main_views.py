from django.conf import settings
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView

from userportal.models import *
from userportal.forms import *
from userportal.tasks import mark_notifications_as_read
from userportal.repositories.enrollment_repository import *
from userportal.repositories.user_repository import *
from userportal.repositories.course_repository import *
from userportal.repositories.notification_repository import *


def index(request):
    # TODO: Swith to the Swagger ui
    context = {
        "somedata": "Hello, world!",
    }
    return render(request, "userportal/index.html", context)


@login_required(login_url="login")
def home(request):
    context = {}
    user = request.user

    if user.is_student():
        context.update(handle_student_view(request, user))
    elif user.is_teacher():
        context.update(handle_teacher_view(user))

    return render(request, "userportal/home.html", context)


def handle_student_view(request, user):
    context = {}
    if request.method == "POST":
        status_form = StatusForm(request.POST)
        if status_form.is_valid():
            status = status_form.cleaned_data["status"]
            if UserRepository.update_student_profile_status(user, status):
                messages.success(request, UPDATE_STATUS_SUCCESS_MSG)
    else:
        initial = {"status": user.student_profile.status}
        status_form = StatusForm(initial=initial)
    context["status_form"] = status_form
    enrollments = EnrollmentRepository.fetch_enrollments_for_student(user)
    (
        context["upcoming_enrollments"],
        context["current_enrollments"],
        context["past_enrollments"],
    ) = enrollments
    return context


def handle_teacher_view(user):
    return {
        "offered_courses": CourseRepository.fetch_teacher_courses(user.teacher_profile)
    }


class NotificationListView(ListView):
    model = Notification
    paginate_by = settings.PAGINATION_PAGE_SIZE
    template_name = "userportal/notification_list.html"
    context_object_name = "notifications"
    login_url = "login"

    def get_queryset(self):
        return NotificationRepository.fetch_notifications_for_user(self.request.user)

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
