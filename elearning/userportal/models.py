from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError


class Program(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=300)

    def __str__(self):
        return self.title


class PortalUserManager(UserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        # email, first_name, last_name and user_type are required fields
        if not email:
            raise ValueError("Email must be specified")
        if not extra_fields.get("first_name"):
            raise ValueError("First name must be specified")
        if not extra_fields.get("last_name"):
            raise ValueError("Last name must be specified")
        if not extra_fields.get("user_type"):
            raise ValueError("User type must be specified")
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

    user_type = models.PositiveSmallIntegerField(
        choices=UserType, blank=True, null=True
    )
    email = models.EmailField(unique=True, blank=True)
    title = models.CharField(max_length=10, choices=Title, blank=True)

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
    registration_date = models.DateField()
    registration_expiry_date = models.DateField(editable=False)

    def save(self, *args, **kwargs):
        self.registration_expiry_date = self.registration_date + relativedelta(years=6)
        super().save(*args, **kwargs)


class TeacherProfile(models.Model):
    user = models.OneToOneField(PortalUser, on_delete=models.CASCADE)
    biography = models.TextField(
        blank=True, null=True, help_text="A professional biography of the teacher"
    )
