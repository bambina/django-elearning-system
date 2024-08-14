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
from django.views.decorators.http import require_POST
from django.conf import settings


def index(request):
    context = {
        "somedata": "Hello, world!",
    }
    return render(request, "userportal/index.html", context)


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


class UserListView(ListView):
    model = PortalUser
    paginate_by = settings.PAGINATION_PAGE_SIZE
    template_name = "userportal/user_list.html"
    context_object_name = "users"
    login_url = "login"

    def get_queryset(self):
        queryset = PortalUser.objects.filter(is_staff=False, is_superuser=False).only(
            "id", "username", "user_type"
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
def home(request):
    next_url = request.POST.get("next") or request.GET.get("next", "/")
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
    context = {"next": next_url, "status_form": status_form}
    return render(request, "userportal/home.html", context)


class UserDetailView(DetailView):
    models = PortalUser
    template_name = "userportal/user_detail.html"
    slug_field = "username"
    slug_url_kwarg = "username"
    login_url = "login"

    def get_object(self):
        username = self.kwargs.get("username")
        return get_object_or_404(PortalUser, username=username)


class CourseListView(ListView):
    model = Course
    paginate_by = settings.PAGINATION_PAGE_SIZE
    template_name = "userportal/course_list.html"
    context_object_name = "courses"
    login_url = "login"

    def get_queryset(self):
        queryset = Course.objects.all().only("id", "title", "description")
        keywords = self.request.GET.get("keywords")
        if keywords:
            query_words = keywords.split()
            q_objects = Q()
            for word in query_words:
                q_objects |= Q(title__icontains=word) | Q(description__icontains=word)
            queryset = queryset.filter(q_objects)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = CourseSearchForm(self.request.GET or None)
        return context


class CourseDetailView(DetailView):
    model = Course
    template_name = "userportal/course_detail.html"
    login_url = "login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        user = self.request.user
        if user.is_student():
            current_term = AcademicTerm.current()
            if current_term:
                context["is_taking"] = CourseOffering.objects.filter(
                    course=course,
                    term=current_term,
                    students__student=user.student_profile,
                ).exists()

            next_term = AcademicTerm.next()
            if next_term:
                upcoming_session = CourseOffering.objects.filter(
                    course=course, term=next_term
                ).first()
                if upcoming_session:
                    context["upcoming_session"] = upcoming_session
                    context["is_enrolled"] = StudentCourseOffering.objects.filter(
                        student=user.student_profile, offering=upcoming_session
                    ).exists()

        context["is_instructor"] = (
            user.is_teacher() and user.teacher_profile == course.teacher
        )

        return context


@login_required(login_url="login")
@require_POST
def enroll_course(request, pk):
    if not request.user.is_student():
        messages.error(request, ERR_ONLY_STUDENTS_CAN_ENROLL)
        return redirect("course-list")

    try:
        offering = CourseOffering.objects.get(id=pk)
        _, created = StudentCourseOffering.objects.get_or_create(
            student=request.user.student_profile, offering=offering
        )
        if created:
            messages.success(request, ENROLL_COURSE_SUCCESS_MSG)
        else:
            messages.warning(request, ALREADY_ENROLLED_MSG)
        return redirect("course-detail", pk=offering.course.id)
    except Course.DoesNotExist:
        messages.error(request, ERR_COURSE_DOES_NOT_EXIST)
        return redirect("course-list")
