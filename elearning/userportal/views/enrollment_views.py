from ..models import *
from ..forms import *
from django.views.generic import ListView
from django.conf import settings


class EnrolledStudentsListView(ListView):
    model = StudentCourseOffering
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

        return StudentCourseOffering.objects.filter(
            offering=current_offering
        ).select_related("student")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = self.kwargs.get("course_id")
        course = Course.objects.get(pk=course_id)
        context["course"] = course
        return context
