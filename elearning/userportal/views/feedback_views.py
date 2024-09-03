from django.shortcuts import redirect
from django.contrib import messages
from ..models import *
from ..forms import *
from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from django.conf import settings
from userportal.repositories import *
from django.views.generic import CreateView
from django.contrib.auth.mixins import UserPassesTestMixin
from userportal.permissions import PermissionChecker


class FeedbackCreateView(UserPassesTestMixin, CreateView):
    """Allows students to leave feedback for a completed course."""

    model = Feedback
    form_class = FeedbackForm
    template_name = "userportal/feedback_create.html"
    login_url = "login"

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, pk=self.kwargs["course_id"])
        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        if has_permission := PermissionChecker.has_finished_course(
            self.request.user, self.course
        ):
            self.student = self.request.user.student_profile
        return has_permission

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = FeedbackRepository.fetch(self.student, self.course)
        return kwargs

    def form_valid(self, form):
        try:
            # Use the repository method to create or update the feedback
            FeedbackRepository.create_or_update(
                form.cleaned_data, self.course, self.student, form.instance
            )
            messages.success(self.request, SAVE_FEEDBACK_SUCCESS_MSG)
            return redirect("home")
        except Exception:
            form.add_error(None, ERR_UNEXPECTED_MSG)
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course"] = self.course
        return context


class FeedbackListView(ListView):
    model = Feedback
    paginate_by = settings.PAGINATION_PAGE_SIZE
    template_name = "userportal/feedback_list.html"
    context_object_name = "feedbacks"
    login_url = "login"

    def get_queryset(self):
        course_id = self.kwargs.get("course_id")
        return FeedbackRepository.fetch_with_student_grade(course_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = self.kwargs.get("course_id")
        context["course"] = get_object_or_404(Course, pk=course_id)
        return context
