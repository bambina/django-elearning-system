from typing import Type

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin

from userportal.forms import *
from userportal.models import *
from userportal.repositories import *
from userportal.views.mixins import QueryParamsMixin

AuthUserType = Type[get_user_model()]


class CourseListView(QueryParamsMixin, ListView):
    model = Course
    paginate_by = settings.PAGINATION_PAGE_SIZE
    template_name = "userportal/course_list.html"
    context_object_name = "courses"

    def get_queryset(self):
        keywords = self.request.GET.get("keywords")
        return CourseRepository.fetch_filtered_by(keywords)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = CourseSearchForm(self.request.GET or None)
        return context


class CourseDetailView(DetailView):
    model = Course
    template_name = "userportal/course_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        course = self.object
        # Add course offering data
        context.update(self.get_course_offerings_context(course))
        # Return early for anonymous users
        if user.is_anonymous:
            return context

        # Add QA session data
        context.update(self.get_qa_session_context(course))
        # Add request user's data
        if user.is_student():
            context.update(self.get_student_context(user.student_profile, context))
        elif user.is_teacher():
            context["is_instructor"] = user.teacher_profile == course.teacher

        return context

    @staticmethod
    def get_course_offerings_context(course: Course) -> dict:
        """Get the current and next course offerings for the given course."""
        return {
            "next_offering": CourseOfferingRepository.fetch_next(course),
            "current_offering": CourseOfferingRepository.fetch_current(course),
        }

    @staticmethod
    def get_student_context(profile: StudentProfile, context: dict) -> dict:
        """Get the student's enrollment status for the current and next course offerings."""
        return {
            "is_taking": EnrollmentRepository.is_enrolled(
                profile, context["current_offering"]
            ),
            "is_registered": EnrollmentRepository.is_enrolled(
                profile, context["next_offering"]
            ),
        }

    @staticmethod
    def get_qa_session_context(course: Course) -> dict:
        """Get the active or ended QA session for the course."""
        qa_session = QASessionRepository.fetch(course)
        return {
            "qa_session": qa_session,
            "show_start_session_button": not qa_session or qa_session.is_ended(),
        }


class CourseCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = "userportal/course_create.html"
    login_url = "login"

    def test_func(self):
        return self.request.user.groups.filter(name=PERMISSION_GROUP_TEACHER).exists()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["teacher"] = self.request.user.teacher_profile
        return kwargs

    def form_valid(self, form):
        try:
            teacher = self.request.user.teacher_profile
            self.object = CourseRepository.create(form.cleaned_data, teacher)
            messages.success(self.request, CREATED_SUCCESS_MSG.format(entity="course"))
            return redirect("course-detail", pk=self.object.pk)
        except Exception:
            form.add_error(None, ERR_UNEXPECTED_MSG)
            return self.form_invalid(form)
