from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash, login
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from .models import *
from .forms import *
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.db.models import Q, Subquery, OuterRef, Case, When, Value
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

    # Prepare the context
    next_url = request.POST.get("next") or request.GET.get("next", "/")
    context = {"next": next_url, "status_form": status_form}

    # Get student's courses
    if request.user.is_student():
        student = request.user.student_profile
        student_offerings = StudentCourseOffering.objects.filter(
            student=student
        ).select_related('offering', 'offering__course', 'offering__term')

        context["upcoming_offerings"] = []
        context["current_offerings"] = []
        context["past_offerings"] = []

        for so in student_offerings:
            if so.offering.term.status == AcademicTerm.TermStatus.NOT_STARTED:
                context["upcoming_offerings"].append(so.offering)
            elif so.offering.term.status == AcademicTerm.TermStatus.IN_PROGRESS:
                context["current_offerings"].append(so.offering)
            else:
                context["past_offerings"].append(so.offering)

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
                next_offering = CourseOffering.objects.filter(
                    course=course, term=next_term
                ).first()
                if next_offering:
                    context["next_offering"] = next_offering
                    context["is_enrolled"] = StudentCourseOffering.objects.filter(
                        student=user.student_profile, offering=next_offering
                    ).exists()

        context["is_instructor"] = (
            user.is_teacher() and user.teacher_profile == course.teacher
        )

        return context


@login_required(login_url="login")
@require_POST
def enroll_course(request, course_id, offering_id):
    if not request.user.is_student():
        messages.error(request, ERR_ONLY_STUDENTS_CAN_ENROLL)
        return redirect("course-list")

    try:
        offering = CourseOffering.objects.get(id=offering_id)
        _, created = StudentCourseOffering.objects.get_or_create(
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


@login_required(login_url="login")
def create_course(request):
    if not request.user.is_teacher():
        messages.error(request, ERR_ONLY_TEACHERS_CAN_CREATE_COURSES)
        return redirect("course-list")

    try:
        teacher_profile = TeacherProfile.objects.get(user=request.user)
    except TeacherProfile.DoesNotExist:
        messages.error(request, ERR_DOES_NOT_EXIST.format(value="TeacherProfile"))
        return redirect("course-list")

    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = teacher_profile
            course.save()
            return redirect("course-detail", pk=course.pk)
    else:
        form = CourseForm()
    return render(request, "userportal/create_course.html", {"form": form})


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
        request, "userportal/create_offering.html", {"form": form, "course": course}
    )

@login_required(login_url="login")
def create_feedback(request, course_id):
    if not request.user.is_student():
        messages.error(request, ERR_ONLY_STUDENTS_CAN_CREATE_FEEDBACK)
        return redirect("course-list")
    pass

    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        messages.error(request, ERR_DOES_NOT_EXIST.format(value="Course"))
        return redirect("course-list")

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
        request, "userportal/create_feedback.html", {"form": form, "course": course}
    )


class FeedbackListView(ListView):
    model = Feedback
    paginate_by = settings.PAGINATION_PAGE_SIZE
    template_name = "userportal/feedback_list.html"
    context_object_name = "feedbacks"
    login_url = "login"

    def get_queryset(self):
        course_id = self.kwargs.get("course_id")

        latest_grade = StudentCourseOffering.objects.filter(
            student=OuterRef("student"),
            offering__course_id=course_id,
            offering__term__end_datetime__lt=now(),
        ).order_by("-offering__term__end_datetime").values("grade")[:1]

        return Feedback.objects.filter(course_id=course_id).annotate(
            grade=Subquery(latest_grade),
            grade_display=Case(
                When(grade=StudentCourseOffering.Grade.PASS, then=Value('Pass')),
                When(grade=StudentCourseOffering.Grade.FAIL, then=Value('Fail')),
                default=Value("Not Graded"),
            )
        ).select_related("student").order_by("-updated_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = self.kwargs.get("course_id")
        course = get_object_or_404(Course, pk=course_id)
        context["course"] = course
        return context

@login_required(login_url="login")
def view_currently_enrolled_students(request, course_id):
    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        messages.error(request, ERR_DOES_NOT_EXIST.format(value="Course"))
        return redirect("course-list")
    
    current_offering = CourseOffering.objects.filter(
        course=course, term__start_datetime__lte=now(), term__end_datetime__gte=now()
    ).first()

    if not current_offering:
        messages.error(request, ERR_NO_CURRENT_OFFERING)
        return redirect("course-detail", pk=course_id)
    
    student_offerings = StudentCourseOffering.objects.filter(
        offering=current_offering
    ).select_related('student')

    return render(
        request, "userportal/student_list.html", {"course": course, "student_offerings": student_offerings}
    )

class EnrolledStudentsListView(ListView):
    model = StudentCourseOffering
    template_name = "userportal/student_list.html"
    context_object_name = "student_offerings"
    paginate_by = settings.PAGINATION_PAGE_SIZE
    login_url = "login"

    def get_queryset(self):
        course_id = self.kwargs.get('course_id')

        current_offering = CourseOffering.objects.filter(
            course_id=course_id, term__start_datetime__lte=now(), term__end_datetime__gte=now()
        ).first()
        
        return StudentCourseOffering.objects.filter(
            offering=current_offering
            ).select_related('student')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = self.kwargs.get('course_id')
        course = Course.objects.get(pk=course_id)
        context['course'] = course
        return context
