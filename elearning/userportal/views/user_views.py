from ..models import *
from ..forms import *
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import Http404


class UserDetailView(DetailView):
    models = get_user_model()
    template_name = "userportal/user_detail.html"
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_object(self):
        username = self.kwargs.get("username")
        user = get_object_or_404(get_user_model(), username=username)
        # Anyone can view teacher profiles
        if user.is_teacher():
            return user
        # Only authenticated users can view profiles
        if self.request.user.is_authenticated:
            return user
        # Raise a 404 error if the user is not authenticated and trying to access a non-teacher profile.
        raise Http404(ERR_USER_NOT_FOUND)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.is_teacher():
            context["offered_courses"] = self.object.teacher_profile.courses.all()
            context["is_instructor"] = self.object == self.request.user
        return context


class UserListView(ListView):
    model = get_user_model()
    paginate_by = settings.PAGINATION_PAGE_SIZE
    template_name = "userportal/user_list.html"
    context_object_name = "users"
    login_url = "login"

    def get_queryset(self):
        queryset = (
            get_user_model()
            .objects.filter(is_staff=False, is_superuser=False)
            .only("id", "username", "user_type")
        )
        keywords = self.request.GET.get("keywords")
        user_types = self.request.GET.getlist("user_type")
        if keywords:
            query_words = keywords.split()
            q_objects = Q()
            for word in query_words:
                q_objects |= (
                    Q(username__icontains=word)
                    | Q(first_name__icontains=word)
                    | Q(last_name__icontains=word)
                    | Q(title__icontains=word)
                )
            queryset = queryset.filter(q_objects)
        if user_types:
            queryset = queryset.filter(user_type__in=user_types)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = UserSearchForm(self.request.GET or None)
        return context


@login_required(login_url="login")
# @permission_required('auth.change_user', raise_exception=True)
def deactivate_user(request, username):
    user = get_object_or_404(get_user_model(), username=username)
    if user.is_active:
        user.is_active = False
        user.save()
        messages.success(request, DEACTIVATE_USER_SUCCESS_MSG.format(username=username))
    else:
        messages.info(request, USER_ALREADY_DEACTIVATED_MSG.format(username=username))
    return redirect("user-list")


@login_required(login_url="login")
# @permission_required('auth.change_user', raise_exception=True)
def activate_user(request, username):
    user = get_object_or_404(get_user_model(), username=username)
    if user.is_active:
        messages.info(request, USER_ALREADY_ACTIVATED_MSG.format(username=username))
    else:
        user.is_active = True
        user.save()
        messages.success(request, ACTIVATE_USER_SUCCESS_MSG.format(username=username))
    return redirect("user-list")
