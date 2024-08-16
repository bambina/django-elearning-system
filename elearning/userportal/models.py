from dateutil.relativedelta import relativedelta

from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError
from django.utils.timezone import now

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

    class Meta:
        ordering = ["username"]


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
        FALL = 1, _("FALL")
        SPRING = 2, _("SPRING")

    class TermStatus(models.IntegerChoices):
        NOT_STARTED = 1, _("Not Started")
        IN_PROGRESS = 2, _("In Progress")
        ENDED = 3, _("Ended")

    semester = models.PositiveSmallIntegerField(choices=SemesterType)
    year = models.PositiveSmallIntegerField()
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    class Meta:
        ordering = ["-start_datetime"]

    @classmethod
    def current(cls):
        return cls.objects.filter(
            start_datetime__lte=now(), end_datetime__gte=now()
        ).first()

    @classmethod
    def next(cls):
        return (
            cls.objects.filter(start_datetime__gt=now())
            .order_by("start_datetime")
            .first()
        )

    @classmethod
    def previous(cls):
        return (
            cls.objects.filter(end_datetime__lt=now()).order_by("-end_datetime").first()
        )

    @property
    def status(self):
        current_time = now()
        if current_time > self.end_datetime:
            return self.TermStatus.ENDED
        elif current_time < self.start_datetime:
            return self.TermStatus.NOT_STARTED
        else:
            return self.TermStatus.IN_PROGRESS

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
        start_date = self.start_datetime.strftime("%b %d %Y")
        end_date = self.end_datetime.strftime("%b %d %Y")
        return f"{self.get_semester_display()} {self.year} ({start_date} - {end_date})"


class Course(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    program = models.ForeignKey(
        "Program", on_delete=models.CASCADE, related_name="courses"
    )
    teacher = models.ForeignKey(
        "TeacherProfile", on_delete=models.CASCADE, related_name="courses"
    )

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class CourseOffering(models.Model):
    course = models.ForeignKey(
        "Course", on_delete=models.CASCADE, related_name="offerings"
    )
    term = models.ForeignKey(
        "AcademicTerm", on_delete=models.CASCADE, related_name="offerings"
    )

    class Meta:
        unique_together = ["course", "term"]

    def __str__(self):
        return f"{self.course} ({self.term})"


class Enrollment(models.Model):
    class Grade(models.IntegerChoices):
        NOT_GRADED = 1, _("Not Graded")
        PASS = 2, _("Pass")
        FAIL = 3, _("Fail")

    student = models.ForeignKey(
        "StudentProfile", on_delete=models.CASCADE, related_name="courses"
    )
    offering = models.ForeignKey(
        "CourseOffering", on_delete=models.CASCADE, related_name="students"
    )
    grade = models.PositiveSmallIntegerField(
        choices=Grade.choices, default=Grade.NOT_GRADED
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["student", "offering"]
        indexes = [
            models.Index(fields=["student", "offering"]),
        ]

    @property
    def status(self):
        current_time = now()
        if current_time > self.offering.term.end_datetime:
            return "Ended"
        elif current_time < self.offering.term.start_datetime:
            return "Registered"
        else:
            return "In Progress"

    def clean(self):
        current_time = now()
        if current_time > self.offering.term.start_datetime:
            raise ValidationError(
                {
                    "offering": ValidationError(
                        f"{INVALID_VALUE_MSG} {INVALID_COURSE_ALREADY_STARTED_MSG}",
                        code=VALIDATION_ERR_INVALID,
                        params={"value": self.offering},
                    )
                }
            )
        if Enrollment.objects.filter(
            student=self.student, offering=self.offering
        ).exists():
            raise ValidationError(
                {
                    "offering": ValidationError(
                        f"{INVALID_VALUE_MSG} {ALREADY_ENROLLED_MSG}",
                        code=VALIDATION_ERR_INVALID,
                        params={"value": self.offering},
                    )
                }
            )

    def __str__(self):
        return f"{self.student} ({self.offering})"


class Feedback(models.Model):
    student = models.ForeignKey(
        "StudentProfile", on_delete=models.CASCADE, related_name="feedbacks"
    )
    course = models.ForeignKey(
        "Course", on_delete=models.CASCADE, related_name="feedbacks"
    )
    comments = models.TextField(max_length=500)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "course")

    def __str__(self):
        return f"{self.student} ({self.course})"
