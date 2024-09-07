from django.conf import settings
from django.contrib import messages
from django.http import FileResponse
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from userportal.forms import *
from userportal.tasks import *
from userportal.models import *
from userportal.repositories import *
from userportal.permissions import PermissionChecker


class CreateMaterialView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Material
    form_class = MaterialForm
    template_name = "userportal/material_create.html"
    login_url = "login"

    def test_func(self):
        self.course = get_object_or_404(Course, pk=self.kwargs["course_id"])
        return PermissionChecker.can_upload_material(self.request.user, self.course)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course"] = self.course
        return context

    def form_valid(self, form):
        try:
            material = MaterialRepository.create(
                form.cleaned_data, self.course, self.request.FILES
            )
            # Asynchronously send notifications to students enrolled in the course
            notify_students_of_material_creation.delay(self.course.id, material.id)
            messages.success(
                self.request, CREATED_SUCCESS_MSG.format(entity="material")
            )
            return redirect("course-detail", pk=self.course.id)
        except Exception:
            form.add_error(None, ERR_UNEXPECTED_MSG)
            return self.form_invalid(form)


class MaterialListView(ListView):
    model = Material
    paginate_by = settings.PAGINATION_PAGE_SIZE
    template_name = "userportal/material_list.html"
    context_object_name = "materials"
    login_url = "login"

    def get_queryset(self):
        course_id = self.kwargs.get("course_id")
        course = get_object_or_404(Course, pk=course_id)
        return MaterialRepository.fetch(course)

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
