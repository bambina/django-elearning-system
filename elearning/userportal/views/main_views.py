from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import *
from ..forms import *

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
        student_offerings = StudentCourseOffering.objects.filter(
            student=student
        ).select_related("offering", "offering__course", "offering__term")

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
