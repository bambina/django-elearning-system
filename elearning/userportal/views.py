from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash, login
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from .models import *
from .forms import *
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.db.models import Q

def index(request):
    context = {
        "somedata": "Hello, world!",
    }
    return render(request, "userportal/index.html", context)


@login_required(login_url="login")
def home(request):
    next_url = request.POST.get("next") or request.GET.get("next", "/")
    context = {"somedata": "Hello, world!", "next": next_url}
    return render(request, "userportal/home.html", context)


def signup(request):
    if request.method == "POST":
        student_form = StudentForm(request.POST)
        student_profile_form = StudentProfileForm(request.POST)
        if student_form.is_valid() and student_profile_form.is_valid():
            student = student_form.save(commit=False)
            student.user_type = PortalUser.UserType.STUDENT
            student.save()
            student_profile = student_profile_form.save(commit=False)
            student_profile.user = student
            student_profile.save()
            messages.success(request, CREATE_STUDENT_ACCOUNT_SUCCESS_MSG)
            login(request, student)
            return redirect("home")
    else:
        student_form = StudentForm()
        student_profile_form = StudentProfileForm()

    context = {
        "student_form": student_form,
        "student_profile_form": student_profile_form,
    }
    return render(request, "registration/signup.html", context)


@login_required(login_url="login")
def password_change(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, PASSWORD_CHANGE_SUCCESS_MSG)
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "registration/password_change.html", {"form": form})


# @login_required(login_url="login")
class UserListView(ListView):
    model = PortalUser
    paginate_by = 3
    template_name = 'userportal/user_list.html'
    context_object_name = 'users'

    def get_queryset(self):
        queryset = PortalUser.objects.filter(is_staff=False, is_superuser=False).only('id', 'username', 'user_type')
        keywords = self.request.GET.get('keywords')
        user_types = self.request.GET.getlist('user_type')
        if keywords:
            query_words = keywords.split()
            q_objects = Q()
            for word in query_words:
                q_objects |= Q(username__icontains=word) | Q(first_name__icontains=word) | Q(last_name__icontains=word) | Q(title__icontains=word)
            queryset = queryset.filter(q_objects)
        if user_types:
            queryset = queryset.filter(user_type__in=user_types)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = UserSearchForm(self.request.GET or None)
        return context

class UserDetailView(DetailView):
    models = PortalUser
    template_name = 'userportal/user_detail.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_object(self):
        username = self.kwargs.get('username')
        return get_object_or_404(PortalUser, username=username)
