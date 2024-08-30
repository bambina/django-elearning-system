from django.utils import timezone
from django.contrib.auth import get_user_model
import factory
from factory.django import DjangoModelFactory

from userportal.models import *
from userportal.tests.utils import get_term_datetimes

User = get_user_model()


class ProgramFactory(DjangoModelFactory):
    class Meta:
        model = Program

    title = factory.Faker("text")
    description = factory.Faker("text")


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    username = factory.Faker("user_name")
    password = factory.PostGenerationMethodCall("set_password", "abc")
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    title = User.Title.PROF
    user_type = User.UserType.TEACHER

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        manager = cls._get_manager(model_class)
        return manager.create_user(*args, **kwargs)

    @factory.post_generation
    def save_user(self, create, extracted, **kwargs):
        if create:
            self.save()


class TeacherProfileFactory(DjangoModelFactory):
    class Meta:
        model = TeacherProfile

    user = factory.SubFactory(UserFactory, user_type=User.UserType.TEACHER)
    biography = factory.Faker("text")


class StudentProfileFactory(DjangoModelFactory):
    class Meta:
        model = StudentProfile

    user = factory.SubFactory(UserFactory, user_type=User.UserType.STUDENT)
    status = factory.Faker("text")
    program = factory.SubFactory(ProgramFactory)


class AcademicTermFactory(DjangoModelFactory):
    class Meta:
        model = AcademicTerm

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        # Get the current term
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

    title = factory.Faker("text")
    description = factory.Faker("text")
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
    comments = factory.Faker("text")


class QASessionFactory(DjangoModelFactory):
    class Meta:
        model = QASession

    course = factory.SubFactory(CourseFactory)
    status = QASession.Status.ACTIVE
    created_at = timezone.now() - timezone.timedelta(hours=1)

    @factory.lazy_attribute
    def room_name(self):
        return f"{self.course.id}_{self.created_at.strftime('%Y%m%d%H%M%S%f')}"


class QAQuestionFactory(DjangoModelFactory):
    class Meta:
        model = QAQuestion

    room_name = factory.Faker("text")
    text = factory.Faker("text")
    sender = factory.Faker("name")
    timestamp = timezone.now() - timezone.timedelta(minutes=5)
