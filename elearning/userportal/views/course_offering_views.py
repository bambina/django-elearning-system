from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import *
from ..forms import *
from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.conf import settings


@login_required(login_url="login")
@require_POST
def enroll_course(request, course_id, offering_id):
    if not request.user.is_student():
        messages.error(request, ERR_ONLY_STUDENTS_CAN_ENROLL)
        return redirect("course-list")

    try:
        offering = CourseOffering.objects.get(id=offering_id)
        _, created = Enrollment.objects.get_or_create(
            student=request.user.student_profile, offering=offering
        )
        if created:
            messages.success(request, ENROLL_COURSE_SUCCESS_MSG)
        else:
            messages.warning(request, ALREADY_ENROLLED_MSG)
        return redirect("course-detail", pk=course_id)
    except Course.DoesNotExist:
        messages.error(request, ERR_DOES_NOT_EXIST.format(value="Course"))
        return redirect("course-list")


class CourseOfferingListView(ListView):
    model = CourseOffering
    paginate_by = settings.PAGINATION_PAGE_SIZE
    template_name = "userportal/offering_list.html"
    context_object_name = "offerings"
    login_url = "login"

    def get_queryset(self):
        course_id = self.kwargs.get("course_id")
        return CourseOffering.objects.filter(course_id=course_id).order_by(
            "-term__start_datetime"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = self.kwargs.get("course_id")
        course = get_object_or_404(Course, pk=course_id)
        context["course"] = course
        return context


@login_required(login_url="login")
def create_course_offering(request, course_id):
    if not request.user.is_teacher():
        messages.error(request, ERR_ONLY_TEACHERS_CAN_CREATE_COURSE_OFFERINGS)
        return redirect("course-list")

    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        messages.error(request, ERR_DOES_NOT_EXIST.format(value="Course"))
        return redirect("course-list")

    if request.method == "POST":
        form = CourseOfferingForm(request.POST, course=course)
        if form.is_valid():
            offering = form.save(commit=False)
            offering.course = course
            offering.save()
            return redirect("offering-list", course_id=course_id)
    else:
        form = CourseOfferingForm(course=course)
    return render(
        request, "userportal/offering_create.html", {"form": form, "course": course}
    )
