from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
import factory
from django.utils import timezone

from userportal.models import *

User = get_user_model()


def get_current_term():
    today = timezone.now().date()
    current_year = today.year
    next_year = current_year + 1
    previous_year = current_year - 1

    # Fall term is from October 1 to March 31
    fall_start = timezone.datetime(previous_year, 10, 1).date()
    fall_end = timezone.datetime(current_year, 3, 31).date()
    # Spring term is from April 1 to September 30
    spring_start = timezone.datetime(current_year, 4, 1).date()
    spring_end = timezone.datetime(current_year, 9, 30).date()
    # Fall term is from October 1 to March 31
    fall_start2 = timezone.datetime(current_year, 10, 1).date()
    fall_end2 = timezone.datetime(next_year, 3, 31).date()

    if fall_start <= today <= fall_end:
        return AcademicTerm(
            semester=AcademicTerm.SemesterType.FALL,
            year=fall_start.year,
            start_datetime=fall_start,
            end_datetime=fall_end,
        )
    elif spring_start <= today <= spring_end:
        return AcademicTerm(
            semester=AcademicTerm.SemesterType.SPRING,
            year=spring_start.year,
            start_datetime=spring_start,
            end_datetime=spring_end,
        )
    else:
        return AcademicTerm(
            semester=AcademicTerm.SemesterType.FALL,
            year=fall_start2.year,
            start_datetime=fall_start2,
            end_datetime=fall_end2,
        )


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
    registration_date = get_current_term().start_datetime
    registration_expiry_date = registration_date.replace(
        year=registration_date.year + 6
    )


class AcademicTermFactory(DjangoModelFactory):
    class Meta:
        model = AcademicTerm

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        # Get the current term
        current_term = get_current_term()
        defaults = {
            "semester": current_term.semester,
            "year": current_term.year,
            "start_datetime": current_term.start_datetime,
            "end_datetime": current_term.end_datetime,
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
