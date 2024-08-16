from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import *
from ..forms import *
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.conf import settings


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
    return render(request, "userportal/course_create.html", {"form": form})
