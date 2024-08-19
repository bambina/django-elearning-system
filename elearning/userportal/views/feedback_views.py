from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import *
from ..forms import *
from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from django.db.models import Subquery, OuterRef, Case, When, Value
from django.conf import settings


@login_required(login_url="login")
def create_feedback(request, course_id):
    if not request.user.is_student():
        messages.error(request, ERR_ONLY_STUDENTS_CAN_CREATE_FEEDBACK)
        return redirect("course-list")
    pass

    course = get_object_or_404(Course, pk=course_id)
    student = request.user.student_profile
    try:
        feedback = Feedback.objects.get(student=student, course=course)
    except Feedback.DoesNotExist:
        feedback = None

    if request.method == "POST":
        form = FeedbackForm(request.POST, instance=feedback)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.course = course
            feedback.student = student
            feedback.save()
            messages.success(request, SAVE_FEEDBACK_SUCCESS_MSG)
            return redirect("home")
    else:
        form = FeedbackForm(instance=feedback)
    return render(
        request, "userportal/feedback_create.html", {"form": form, "course": course}
    )


class FeedbackListView(ListView):
    model = Feedback
    paginate_by = settings.PAGINATION_PAGE_SIZE
    template_name = "userportal/feedback_list.html"
    context_object_name = "feedbacks"
    login_url = "login"

    def get_queryset(self):
        course_id = self.kwargs.get("course_id")

        latest_grade = (
            Enrollment.objects.filter(
                student=OuterRef("student"),
                offering__course_id=course_id,
                offering__term__end_datetime__lt=now(),
            )
            .order_by("-offering__term__end_datetime")
            .values("grade")[:1]
        )

        return (
            Feedback.objects.filter(course_id=course_id)
            .annotate(
                grade=Subquery(latest_grade),
                grade_display=Case(
                    When(grade=Enrollment.Grade.PASS, then=Value("Pass")),
                    When(grade=Enrollment.Grade.FAIL, then=Value("Fail")),
                    default=Value("Not Graded"),
                ),
            )
            .select_related("student")
            .order_by("-updated_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = self.kwargs.get("course_id")
        context["course"] = get_object_or_404(Course, pk=course_id)
        return context
