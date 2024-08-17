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

            # Notify students enrolled in the course
            # TODO:
            # Asynchronously send notifications to students
            students = StudentProfile.objects.filter(
                courses__offering__course=course,
                courses__offering__term=AcademicTerm.current(),
            ).only("user")
            users = [student.user for student in students]
            link_path = reverse("material-list", kwargs={"course_id": course_id})
            link_text = "View Materials"
            message = f"A new material '{material.title}' has been added to the course '{course.title}'."
            send_notification(users, message, link_path, link_text)

            messages.success(request, MATERIAL_CREATED_SUCCESS_MSG)
            return redirect("course-detail", pk=course_id)
    else:
        form = MaterialForm()
    return render(
        request, "userportal/material_create.html", {"course": course, "form": form}
    )


def send_notification(users, message, link_path, link_text):
    for user in users:
        Notification.objects.create(
            user=user, message=message, link_path=link_path, link_text=link_text
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
