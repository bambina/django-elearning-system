from dateutil.relativedelta import relativedelta

from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.core.validators import FileExtensionValidator

from .constants import *
from .validators import *
from .utils import path_and_rename
from userportal.tests.utils import *


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
                VALIDATION_ERR_MISSING_FIELD.format(entity="Email"),
                code=VALIDATION_ERR_REQUIRED,
            )

        for field_name in ["first_name", "last_name", "user_type"]:
            if not extra_fields.get(field_name):
                errors[field_name] = ValidationError(
                    VALIDATION_ERR_MISSING_FIELD.format(entity=field_name.capitalize()),
                    code=VALIDATION_ERR_REQUIRED,
                )

        if errors:
            raise ValidationError(errors)

        return super().create_user(username, email, password, **extra_fields)


class PortalUser(AbstractUser):
    class UserType(models.IntegerChoices):
        TEACHER = 1, _("Teacher")
        STUDENT = 2, _("Student")

    class Title(models.TextChoices):
        PREFER_NOT_TO_SAY = "NONE", _("")
        MR = "MR", _("Mr.")
        MS = "MS", _("Ms.")
        MRS = "MRS", _("Mrs.")
        DR = "DR", _("Dr.")
        PROF = "PROF", _("Prof.")

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
            title = self.get_title_display() if self.title else ""
            return f"{title} {self.first_name} {self.last_name}".strip()
        else:
            return super().__str__()

    class Meta:
        ordering = ["username"]


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


class StudentProfile(models.Model):
    user = models.OneToOneField(
        PortalUser, on_delete=models.CASCADE, related_name="student_profile"
    )
    status = models.CharField(max_length=100, blank=True)
    program = models.ForeignKey(
        Program, on_delete=models.CASCADE, related_name="students"
    )
    registration_date = models.DateField(editable=False)
    registration_expiry_date = models.DateField(editable=False)

    def save(self, *args, **kwargs):
        self.registration_date = get_registration_date()
        self.registration_expiry_date = self.registration_date + relativedelta(years=6)
        super().save(*args, **kwargs)

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
        start_date = self.start_datetime.strftime("%b %d, %Y")
        end_date = self.end_datetime.strftime("%b %d, %Y")
        return f"{self.get_semester_display()} {self.year} ({start_date} to {end_date})"


class Course(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    program = models.ForeignKey(
        Program, on_delete=models.CASCADE, related_name="courses"
    )
    teacher = models.ForeignKey(
        TeacherProfile, on_delete=models.CASCADE, related_name="courses"
    )

    class Meta:
        ordering = ["title"]
        unique_together = ["title", "program"]

    def __str__(self):
        return self.title


class CourseOffering(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="offerings"
    )
    term = models.ForeignKey(
        AcademicTerm, on_delete=models.CASCADE, related_name="offerings"
    )

    class Meta:
        unique_together = ["course", "term"]

    def __str__(self):
        return f"{self.course} - {self.term}"


class Enrollment(models.Model):
    class Grade(models.IntegerChoices):
        NOT_GRADED = 1, _("Not Graded")
        PASS = 2, _("Pass")
        FAIL = 3, _("Fail")

    student = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name="enrollments"
    )
    offering = models.ForeignKey(
        CourseOffering, on_delete=models.CASCADE, related_name="enrollments"
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
        errors = {}
        if now() > self.offering.term.start_datetime:
            errors["offering_started"] = ValidationError(
                f"{INVALID_VALUE_MSG} {INVALID_COURSE_ALREADY_STARTED_MSG}",
                code=VALIDATION_ERR_INVALID,
                params={"value": self.offering},
            )
        if Enrollment.objects.filter(
            student=self.student, offering=self.offering
        ).exists():
            errors["enrollment_duplicate"] = ValidationError(
                f"{INVALID_VALUE_MSG} {ALREADY_ENROLLED_MSG}",
                code=VALIDATION_ERR_INVALID,
                params={"value": self.offering},
            )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.student} ({self.offering})"


class Feedback(models.Model):
    student = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name="feedbacks"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="feedbacks"
    )
    comments = models.TextField(max_length=500)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "course")

    def __str__(self):
        return f"{self.student} ({self.course})"


class Material(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    original_filename = models.CharField(max_length=255, blank=True)
    file = models.FileField(
        upload_to=path_and_rename,
        validators=[
            FileExtensionValidator(allowed_extensions=ALLOWED_MATERIAL_EXTENSIONS),
            file_size_validator,
        ],
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="materials"
    )

    class Meta:
        ordering = ["-uploaded_at"]

    def save(self, *args, **kwargs):
        if not self.id:
            self.original_filename = self.file.name
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Notification(models.Model):
    user = models.ForeignKey(
        PortalUser, on_delete=models.CASCADE, related_name="notifications"
    )
    message = models.TextField(max_length=500)
    link_path = models.CharField(max_length=100, blank=True, null=True)
    link_text = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def clean(self):
        # Ensure that both link_path and link_text are provided together
        if (self.link_path or self.link_text) and not (
            self.link_path and self.link_text
        ):
            raise ValidationError(
                {
                    "link_path": ValidationError(
                        f"{INVALID_VALUE_MSG} {ERR_MISSING_NOTIFICATION_LINK}",
                        code=VALIDATION_ERR_INVALID,
                    )
                }
            )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} ({self.message[:20]}...)"


class QASession(models.Model):
    class Status(models.IntegerChoices):
        ACTIVE = 1, _("Active")
        ENDED = 2, _("Ended")

    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="qa_sessions"
    )
    room_name = models.CharField(max_length=200, unique=True, blank=True)
    status = models.PositiveSmallIntegerField(
        choices=Status.choices, default=Status.ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def is_active(self):
        return self.status == self.Status.ACTIVE

    def is_ended(self):
        return self.status == self.Status.ENDED


class QAQuestion(models.Model):
    room_name = models.CharField(max_length=200)
    text = models.TextField()
    # sender is a concatenated string of the User's title, first name, and last name.
    sender = models.CharField(max_length=310, blank=True, null=True)
    timestamp = models.DateTimeField()

    class Meta:
        ordering = ["-timestamp"]
