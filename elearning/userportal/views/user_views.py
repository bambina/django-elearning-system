from django.conf import settings
from django.http import Http404
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_http_methods
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required

from userportal.repositories import *
from userportal.models import *
from userportal.forms import *
from userportal.views.mixins import QueryParamsMixin

AuthUser = get_user_model()


class UserListView(
    LoginRequiredMixin, PermissionRequiredMixin, QueryParamsMixin, ListView
):
    model = AuthUser
    paginate_by = settings.PAGINATION_PAGE_SIZE
    template_name = "userportal/user_list.html"
    context_object_name = "users"
    login_url = "login"
    permission_required = "userportal.view_portaluser"

    def get_queryset(self):
        keywords = self.request.GET.get("keywords")
        user_types = self.request.GET.getlist("user_type")
        return UserRepository.fetch_filtered_by(keywords, user_types)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = UserSearchForm(self.request.GET or None)
        return context


class UserDetailView(DetailView):
    models = AuthUser
    template_name = "userportal/user_detail.html"
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_object(self):
        username = self.kwargs.get("username")
        user = get_object_or_404(AuthUser, username=username)
        # Anyone can view teacher profiles
        if user.is_teacher():
            return user
        # Only authenticated users can view profiles
        if self.request.user.is_authenticated:
            return user
        # Raise a 404 error if the user is not authenticated and trying to access a non-teacher profile.
        raise Http404

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add student's enrollment data categorized into upcoming, current, and past enrollments.
        user = self.object
        if user.is_student():
            enrollments = EnrollmentRepository.fetch(user.student_profile)
            # Unpack the enrollments tuple into context
            (
                context["upcoming_enrollments"],
                context["current_enrollments"],
                context["past_enrollments"],
            ) = enrollments
        # Add a list of courses that the teacher is currently offering.
        if user.is_teacher():
            context["offered_courses"] = user.teacher_profile.courses.all()

        return context


@require_http_methods(["POST"])
@login_required(login_url="login")
@permission_required("userportal.change_portaluser", raise_exception=True)
def toggle_active_status(request, username, activate):
    activate = activate.lower() == "true"
    action = "activated" if activate else "deactivated"
    try:
        is_toggled = UserRepository.toggle_user_active_status(
            username, activate=activate
        )
    except Exception:
        messages.error(
            request, ERR_UPDATE_USER_ACTIVE_STATUS_FAIL.format(username=username)
        )
        return redirect("user-list")

    if is_toggled:
        messages.success(
            request,
            UPDATE_USER_ACTIVE_STATUS_SUCCESS_MSG.format(
                username=username, action=action
            ),
        )
    else:
        messages.info(
            request, USER_ALREADY_CHANGED_MSG.format(username=username, action=action)
        )
    return redirect("user-list")
