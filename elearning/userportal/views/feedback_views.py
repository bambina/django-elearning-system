from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import *
from ..forms import *
from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from django.conf import settings
from userportal.repositories import *


@login_required(login_url="login")
def create_feedback(request, course_id):
    if not request.user.is_student():
        messages.error(request, ERR_ONLY_STUDENTS_CAN_CREATE_FEEDBACK)
        return redirect("course-list")

    course = get_object_or_404(Course, pk=course_id)
    student = request.user.student_profile
    feedback = FeedbackRepository.get_or_none(student, course)

    if request.method == "POST":
        form = FeedbackForm(request.POST, instance=feedback)
        if form.is_valid():
            FeedbackRepository.create(form.cleaned_data, course, student)
            messages.success(request, SAVE_FEEDBACK_SUCCESS_MSG)
            return redirect("home")
    else:
        form = FeedbackForm(instance=feedback)
    context = {"form": form, "course": course}
    return render(request, "userportal/feedback_create.html", context)


class FeedbackListView(ListView):
    model = Feedback
    paginate_by = settings.PAGINATION_PAGE_SIZE
    template_name = "userportal/feedback_list.html"
    context_object_name = "feedbacks"
    login_url = "login"

    def get_queryset(self):
        course_id = self.kwargs.get("course_id")
        return FeedbackRepository.get_with_student_grade(course_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = self.kwargs.get("course_id")
        context["course"] = get_object_or_404(Course, pk=course_id)
        return context
