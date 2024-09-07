from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, View
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator, login_required
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin

from userportal.forms import *
from userportal.models import *
from userportal.constants import *
from userportal.repositories import *
from userportal.permissions import PermissionChecker
from userportal.tasks import notify_teacher_of_new_enrollment


class CourseOfferingListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = CourseOffering
    paginate_by = settings.PAGINATION_PAGE_SIZE
    template_name = "userportal/offering_list.html"
    context_object_name = "offerings"
    login_url = "login"

    def test_func(self):
        self.course = get_object_or_404(Course, pk=self.kwargs.get("course_id"))
        return PermissionChecker.is_course_admin(self.request.user, self.course)

    def get_queryset(self):
        return CourseOfferingRepository.fetch_with_academic_terms(self.course.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course"] = get_object_or_404(Course, pk=self.course.id)
        return context


@login_required(login_url="login")
def create_course_offering(request, course_id):
    if not request.user.is_teacher():
        messages.error(request, ERR_ONLY_TEACHERS_CAN_CREATE_COURSE_OFFERINGS)
        return redirect("course-list")

    course = get_object_or_404(Course, pk=course_id)

    if request.method == "POST":
        form = CourseOfferingForm(request.POST, course=course)
        if form.is_valid():
            try:
                CourseOfferingRepository.create(form.cleaned_data, course)
                messages.success(
                    request, CREATED_SUCCESS_MSG.format(entity="course offering")
                )
                return redirect("offering-list", course_id=course_id)
            except Exception:
                form.add_error(None, ERR_UNEXPECTED_MSG)
    else:
        form = CourseOfferingForm(course=course)
    context = {"form": form, "course": course}
    return render(request, "userportal/offering_create.html", context=context)


class EnrollCourseView(UserPassesTestMixin, View):
    """Allows students enrolls in a next course offering."""

    login_url = "login"

    def test_func(self):
        return self.request.user.groups.filter(name=PERMISSION_GROUP_STUDENT).exists()

    @method_decorator(require_POST)
    def post(self, request, course_id, offering_id):
        """
        Student enrolls in a next course offering.
        """
        course = get_object_or_404(Course, pk=course_id)
        offering = get_object_or_404(CourseOffering, pk=offering_id)

        _, created = Enrollment.objects.get_or_create(
            student=request.user.student_profile, offering=offering
        )
        if created:
            messages.success(request, ENROLL_COURSE_SUCCESS_MSG)
            # Send a notification to the course teacher
            notify_teacher_of_new_enrollment.delay(
                course.id, offering.id, request.user.username
            )
        else:
            messages.warning(request, ALREADY_ENROLLED_MSG)

        return redirect("course-detail", pk=course.id)


class EnrolledStudentListView(ListView):
    model = Enrollment
    template_name = "userportal/student_list.html"
    context_object_name = "enrollments"
    paginate_by = settings.PAGINATION_PAGE_SIZE

    def get_queryset(self):
        offering_id = self.kwargs.get("offering_id")
        return EnrollmentRepository.fetch_with_student(offering_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        offering_id = self.kwargs.get("offering_id")
        context["offering"] = get_object_or_404(CourseOffering, pk=offering_id)
        return context
