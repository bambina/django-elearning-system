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
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods


class CourseListView(ListView):
    model = Course
    paginate_by = settings.PAGINATION_PAGE_SIZE
    template_name = "userportal/course_list.html"
    context_object_name = "courses"

    def get_queryset(self):
        queryset = Course.objects.select_related("teacher__user").only(
            "id",
            "title",
            "description",
            "teacher__user__title",
            "teacher__user__first_name",
            "teacher__user__last_name",
        )
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_anonymous:
            return context

        course = self.object

        current_term = AcademicTerm.current()
        if current_term:
            current_offering = CourseOffering.objects.filter(
                course=course, term=current_term
            ).first()
            if current_offering:
                context["current_offering"] = current_offering
                if user.is_student():
                    context["is_taking"] = Enrollment.objects.filter(
                        student=user.student_profile, offering=current_offering
                    ).exists()

        next_term = AcademicTerm.next()
        if next_term:
            next_offering = CourseOffering.objects.filter(
                course=course, term=next_term
            ).first()
            if next_offering:
                context["next_offering"] = next_offering
                if user.is_student():
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

    teacher_profile = get_object_or_404(TeacherProfile, user=request.user)

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

    course = get_object_or_404(Course, pk=course_id)

    if request.method == "POST":
        form = MaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.course = course
            material.save()

            # Asynchronously send notifications to students enrolled in the course
            # TODO: Compose message in async task
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
        return Material.objects.filter(course_id=course_id).only(
            "id", "title", "description", "uploaded_at", "file"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course"] = get_object_or_404(Course, pk=self.kwargs.get("course_id"))
        return context


def download_material(request, course_id, material_id):
    course = get_object_or_404(Course, pk=course_id)
    material = get_object_or_404(Material, pk=material_id)

    if not material.file:
        messages.error(request, ERR_DOES_NOT_EXIST.format(entity="file"))
        return redirect("material-list", course_id=course.id)

    response = FileResponse(material.file, as_attachment=True)
    response["Content-Disposition"] = (
        f'attachment; filename="{material.original_filename}"'
    )
    return response


@require_http_methods(["POST"])
def start_qa_session(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

    # Only teachers can start a QA session
    # TODO: Check if the user is the teacher of the course or an admin

    return render(request, "userportal/qa_session.html", {"course": course})
