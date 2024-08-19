from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import *
from ..forms import *

from django.views.generic import ListView
from django.conf import settings

from ..tasks import mark_notifications_as_read
from userportal.repositories.enrollment_repository import *


def index(request):
    context = {
        "somedata": "Hello, world!",
    }
    return render(request, "userportal/index.html", context)


@login_required(login_url="login")
def home(request):
    if request.method == "POST":
        status_form = StatusForm(request.POST)
        if status_form.is_valid():
            pass
            student_profile = request.user.student_profile
            student_profile.status = status_form.cleaned_data["status"]
            student_profile.save()
            messages.success(request, UPDATE_STATUS_SUCCESS_MSG)
    else:
        status = (
            request.user.student_profile.status if request.user.is_student() else ""
        )
        initial = {"status": status}
        status_form = StatusForm(initial=initial)

    # Prepare the context
    next_url = request.POST.get("next") or request.GET.get("next", "/")
    context = {"next": next_url, "status_form": status_form}

    # Get student's courses
    if request.user.is_student():
        enrollments = fetch_enrollments_for_student(request.user)
        (
            context["upcoming_enrollments"],
            context["current_enrollments"],
            context["past_enrollments"],
        ) = enrollments

    # Get teacher's courses
    if request.user.is_teacher():
        teacher = request.user.teacher_profile
        context["offered_courses"] = teacher.courses.all()

    return render(request, "userportal/home.html", context)


class NotificationListView(ListView):
    model = Notification
    paginate_by = settings.PAGINATION_PAGE_SIZE
    template_name = "userportal/notification_list.html"
    context_object_name = "notifications"
    login_url = "login"

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Search for new notifications and mark them as read
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
