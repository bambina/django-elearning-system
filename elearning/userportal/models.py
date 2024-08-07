from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from dateutil.relativedelta import relativedelta
from .validators import *
from django.utils.translation import gettext as _
from .constants import *


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
        NONE = ""
        MR = "Mr."
        MS = "Ms."
        MRS = "Mrs."
        DR = "Dr."
        PROF = "Prof."

    user_type = models.PositiveSmallIntegerField(choices=UserType, null=True)
    email = models.EmailField(unique=True, null=True)
    title = models.CharField(max_length=10, choices=Title, null=True, blank=True)

    objects = PortalUserManager()
    EMAIL_FIELD = "email"

    def is_teacher(self):
        return self.user_type == self.UserType.TEACHER

    def is_student(self):
        return self.user_type == self.UserType.STUDENT

    def __str__(self):
        if self.user_type:
            return f"{self.title} {super().get_full_name()}".strip()
        return super().__str__()


class StudentProfile(models.Model):
    user = models.OneToOneField(PortalUser, on_delete=models.CASCADE)
    status = models.CharField(max_length=100, blank=True)
    program = models.ForeignKey(
        "Program", on_delete=models.CASCADE, related_name="students"
    )
    registration_date = models.DateField(validators=[registration_date_validator])
    registration_expiry_date = models.DateField(editable=False)

    def save(self, *args, **kwargs):
        self.registration_expiry_date = self.registration_date + relativedelta(years=6)
        super().save(*args, **kwargs)


class TeacherProfile(models.Model):
    user = models.OneToOneField(PortalUser, on_delete=models.CASCADE)
    biography = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        help_text="A professional biography of the teacher",
    )
