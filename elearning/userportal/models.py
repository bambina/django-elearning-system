from dateutil.relativedelta import relativedelta

from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError

from .constants import *
from .validators import *


class Program(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)

    def __str__(self):
        return self.title


class PortalUserManager(UserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        # email, first_name, last_name and user_type are required fields
        errors = {}
        if not email:
            errors["email"] = ValidationError(
                _("Email must be specified"), code=VALIDATION_ERR_REQUIRED
            )

        if not extra_fields.get("first_name"):
            errors["first_name"] = ValidationError(
                _("First name must be specified"), code=VALIDATION_ERR_REQUIRED
            )

        if not extra_fields.get("last_name"):
            errors["last_name"] = ValidationError(
                _("Last name must be specified"), code=VALIDATION_ERR_REQUIRED
            )

        if not extra_fields.get("user_type"):
            errors["user_type"] = ValidationError(
                _("User type must be specified"), code=VALIDATION_ERR_REQUIRED
            )

        if errors:
            raise ValidationError(errors)

        return super().create_user(username, email, password, **extra_fields)


class PortalUser(AbstractUser):
    class UserType(models.IntegerChoices):
        TEACHER = 1
        STUDENT = 2

    class Title(models.TextChoices):
        PREFER_NOT_TO_SAY = ""
        MR = "Mr."
        MS = "Ms."
        MRS = "Mrs."
        DR = "Dr."
        PROF = "Prof."

    email = models.EmailField(unique=True, null=True, blank=True)
    user_type = models.PositiveSmallIntegerField(
        choices=UserType, null=True, blank=True
    )
    title = models.CharField(max_length=10, choices=Title, null=True, blank=True)

    objects = PortalUserManager()
    EMAIL_FIELD = "email"

    def is_teacher(self):
        return self.user_type == self.UserType.TEACHER

    def is_student(self):
        return self.user_type == self.UserType.STUDENT

    def get_full_name(self) -> str:
        if self.user_type:
            title = self.title if self.title else ""
            return f"{title} {self.first_name} {self.last_name}".strip()
        else:
            return super().__str__()


class StudentProfile(models.Model):
    user = models.OneToOneField(
        PortalUser, on_delete=models.CASCADE, related_name="student_profile"
    )
    status = models.CharField(max_length=100, blank=True)
    program = models.ForeignKey(
        "Program", on_delete=models.CASCADE, related_name="students"
    )
    registration_date = models.DateField(validators=[registration_date_validator])
    registration_expiry_date = models.DateField(editable=False)

    def save(self, *args, **kwargs):
        self.registration_expiry_date = self.registration_date + relativedelta(years=6)
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.user)


class TeacherProfile(models.Model):
    user = models.OneToOneField(
        PortalUser, on_delete=models.CASCADE, related_name="teacher_profile"
    )
    biography = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        help_text="A professional biography of the teacher",
    )

    def __str__(self):
        return str(self.user)


class AcademicTerm(models.Model):
    class SemesterType(models.IntegerChoices):
        FALL = 1
        SPRING = 2

    semester = models.PositiveSmallIntegerField(choices=SemesterType)
    year = models.PositiveSmallIntegerField()
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    def is_active(self):
        return self.start_datetime <= date.today() <= self.end

    def clean(self):
        if self.start_datetime > self.end_datetime:
            raise ValidationError(
                {
                    "start_datetime": ValidationError(
                        f"{INVALID_VALUE_MSG} {INVALID_START_DATETIME_MSG}",
                        code=VALIDATION_ERR_INVALID,
                        params={"value": self.start_datetime},
                    )
                }
            )

    def __str__(self):
        return f"{self.get_semester_type_display()} {self.year}"


class Course(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    program = models.ForeignKey(
        "Program", on_delete=models.CASCADE, related_name="courses"
    )
    teacher = models.ForeignKey(
        "TeacherProfile", on_delete=models.CASCADE, related_name="courses"
    )

    def __str__(self):
        return self.title


class CourseOffering(models.Model):
    course = models.ForeignKey(
        "Course", on_delete=models.CASCADE, related_name="offerings"
    )
    term = models.ForeignKey(
        "AcademicTerm", on_delete=models.CASCADE, related_name="offerings"
    )

    def __str__(self):
        return f"{self.course} ({self.term})"
