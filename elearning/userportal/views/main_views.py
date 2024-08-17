from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import *
from ..forms import *

from django.views.generic import ListView
from django.conf import settings


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
        student = request.user.student_profile
        student_offerings = Enrollment.objects.filter(student=student).select_related(
            "offering", "offering__course", "offering__term"
        )

        context["upcoming_offerings"] = []
        context["current_offerings"] = []
        context["past_offerings"] = []

        for so in student_offerings:
            if so.offering.term.status == AcademicTerm.TermStatus.NOT_STARTED:
                context["upcoming_offerings"].append(so.offering)
            elif so.offering.term.status == AcademicTerm.TermStatus.IN_PROGRESS:
                context["current_offerings"].append(so.offering)
            else:
                context["past_offerings"].append(so.offering)

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
        page_obj = context.get("page_obj")
        if page_obj:
            # TODO:
            # Asynchronously mark notifications as read
            for notification in page_obj.object_list:
                if not notification.is_read:
                    notification.is_read = True
                    notification.save()
        return context
