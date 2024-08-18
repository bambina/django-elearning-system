from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import *
from ..forms import *
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.conf import settings
from django.http import FileResponse
from django.urls import reverse
from ..tasks import create_notifications_for_enrolled_students


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
                    context["is_enrolled"] = Enrollment.objects.filter(
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


@login_required(login_url="login")
def create_material(request, course_id):
    if not request.user.is_teacher():
        messages.error(request, ERR_ONLY_TEACHERS_CAN_CREATE_MATERIALS)
        return redirect("course-list")

    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        messages.error(request, ERR_DOES_NOT_EXIST.format(value="Course"))
        return redirect("course-list")

    if request.method == "POST":
        form = MaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.course = course
            material.save()

            # Asynchronously send notifications to students enrolled in the course
            message = MATERIAL_CREATED_NOTIFICATION_MSG % {
                "material_title": material.title,
                "course_title": course.title,
            }
            create_notifications_for_enrolled_students.delay(
                course_id,
                message,
                reverse("material-list", kwargs={"course_id": course_id}),
                MATERIAL_CREATED_NOTIFICATION_LINK_TEXT,
            )
            messages.success(request, MATERIAL_CREATED_SUCCESS_MSG)
            return redirect("course-detail", pk=course_id)
    else:
        form = MaterialForm()
    return render(
        request, "userportal/material_create.html", {"course": course, "form": form}
    )


class MaterialListView(ListView):
    model = Material
    paginate_by = settings.PAGINATION_PAGE_SIZE
    template_name = "userportal/material_list.html"
    context_object_name = "materials"
    login_url = "login"

    def get_queryset(self):
        course_id = self.kwargs.get("course_id")
        return Material.objects.filter(course_id=course_id).only("id", "title", "file")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course"] = Course.objects.get(pk=self.kwargs.get("course_id"))
        return context


def download_material(request, course_id, material_id):
    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        messages.error(request, ERR_DOES_NOT_EXIST.format(value="Course"))
        return redirect("course-list")

    try:
        material = Material.objects.get(pk=material_id)
    except Material.DoesNotExist:
        messages.error(request, ERR_DOES_NOT_EXIST.format(value="Material"))
        return redirect("material-list", course_id=course_id)

    if not material.file:
        messages.error(request, ERR_DOES_NOT_EXIST.format(value="Material file"))
        return redirect("material-list", course_id=course_id)

    response = FileResponse(material.file, as_attachment=True)
    response["Content-Disposition"] = (
        f'attachment; filename="{material.original_filename}"'
    )
    return response

class EnrolledStudentListView(ListView):
    model = Enrollment
    template_name = "userportal/student_list.html"
    context_object_name = "student_offerings"
    paginate_by = settings.PAGINATION_PAGE_SIZE
    login_url = "login"

    def get_queryset(self):
        course_id = self.kwargs.get("course_id")

        current_offering = CourseOffering.objects.filter(
            course_id=course_id,
            term__start_datetime__lte=now(),
            term__end_datetime__gte=now(),
        ).first()

        return Enrollment.objects.filter(offering=current_offering).select_related(
            "student"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = self.kwargs.get("course_id")
        course = Course.objects.get(pk=course_id)
        context["course"] = course
        return context
