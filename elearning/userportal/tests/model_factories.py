import factory
from factory.django import DjangoModelFactory

from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.contrib.auth.models import Group

from userportal.models import *
from userportal.tests.utils import get_term_datetimes

AuthUser = get_user_model()


class ProgramFactory(DjangoModelFactory):
    class Meta:
        model = Program

    title = factory.Faker("catch_phrase")
    description = factory.Faker("paragraph")


class UserFactory(DjangoModelFactory):
    class Meta:
        model = AuthUser
        skip_postgeneration_save = True

    username = factory.Faker("user_name")
    password = factory.PostGenerationMethodCall("set_password", "abc")
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    title = AuthUser.Title.PROF
    user_type = AuthUser.UserType.TEACHER

    @factory.post_generation
    def save_user(self, create, extracted, **kwargs):
        if create:
            self.save()

    @factory.post_generation
    def add_group(self, create, extracted, **kwargs):
        if not create:
            return

        if self.user_type == get_user_model().UserType.TEACHER:
            group, _ = Group.objects.get_or_create(name=PERMISSION_GROUP_TEACHER)
        elif self.user_type == get_user_model().UserType.STUDENT:
            group, _ = Group.objects.get_or_create(name=PERMISSION_GROUP_STUDENT)

        self.groups.add(group)
        self.save()


class TeacherProfileFactory(DjangoModelFactory):
    class Meta:
        model = TeacherProfile

    user = factory.SubFactory(UserFactory, user_type=AuthUser.UserType.TEACHER)
    biography = factory.Faker("text")


class StudentProfileFactory(DjangoModelFactory):
    class Meta:
        model = StudentProfile

    user = factory.SubFactory(UserFactory, user_type=AuthUser.UserType.STUDENT)
    status = factory.Faker("text")
    program = factory.SubFactory(ProgramFactory)


class AcademicTermFactory(DjangoModelFactory):
    class Meta:
        model = AcademicTerm

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        # Get the current term data
        semester_val, year, start, end = get_term_datetimes()
        defaults = {
            "semester": AcademicTerm.SemesterType(semester_val),
            "year": year,
            "start_datetime": start,
            "end_datetime": end,
        }
        # Update defaults with any keyword arguments passed
        defaults.update(kwargs)
        return super()._create(model_class, *args, **defaults)


class CourseFactory(DjangoModelFactory):
    class Meta:
        model = Course

    title = factory.Faker("catch_phrase")
    description = factory.Faker("paragraph")
    program = factory.SubFactory(ProgramFactory)
    teacher = factory.SubFactory(TeacherProfileFactory)


class CourseOfferingFactory(DjangoModelFactory):
    class Meta:
        model = CourseOffering

    course = factory.SubFactory(CourseFactory)
    term = factory.SubFactory(AcademicTermFactory)


class EnrollmentFactory(DjangoModelFactory):
    class Meta:
        model = Enrollment

    student = factory.SubFactory(StudentProfileFactory)
    offering = factory.SubFactory(CourseOfferingFactory)
    grade = Enrollment.Grade.NOT_GRADED

    @factory.lazy_attribute
    def enrolled_at(self):
        return self.offering.term.start_datetime - timezone.timedelta(days=20)


class FeedbackFactory(DjangoModelFactory):
    class Meta:
        model = Feedback

    student = factory.SubFactory(StudentProfileFactory)
    course = factory.SubFactory(CourseFactory)
    comments = factory.Faker("sentence")


class MaterialFactory(DjangoModelFactory):
    class Meta:
        model = Material
        skip_postgeneration_save = True

    title = factory.Faker("text", max_nb_chars=100)
    description = factory.Faker("paragraph")
    original_filename = factory.Faker("file_name", extension="pdf")
    file = factory.django.FileField(filename="test.pdf")
    course = factory.SubFactory(CourseFactory)

    @factory.post_generation
    def create_file(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.file = extracted
        else:
            content = ContentFile(b"Dummy file content")
            self.file.save("test.png", content, save=False)
        self.save()


class NotificationFactory(DjangoModelFactory):
    class Meta:
        model = Notification

    user = factory.SubFactory(UserFactory)
    message = factory.Faker("text", max_nb_chars=500)
    link_path = factory.Faker("file_path", depth=2, extension=[])
    link_text = factory.Faker("text", max_nb_chars=100)


class QASessionFactory(DjangoModelFactory):
    class Meta:
        model = QASession

    course = factory.SubFactory(CourseFactory)
    created_at = timezone.now()

    @factory.lazy_attribute
    def room_name(self):
        return generate_unique_room_name(self.course.id)


class QAQuestionFactory(DjangoModelFactory):
    class Meta:
        model = QAQuestion

    room_name = factory.Faker("text")
    text = factory.Faker("text")
    sender = factory.Faker("name")
    timestamp = timezone.now()
