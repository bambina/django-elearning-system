import os
import tempfile
from dateutil.relativedelta import relativedelta

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from userportal.models import *
from userportal.tests.model_factories import *
from userportal.tests.mixins import TermTestMixin

User = get_user_model()


class UserModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.common_password = "abc"

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            username="admin",
            password=self.common_password,
        )
        self.assertEqual(admin.username, "admin")
        self.assertTrue(admin.check_password(self.common_password))
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_create_user_with_required_fields(self):
        user = UserFactory.create(
            username="user",
            password=self.common_password,
            email="a@example.com",
            first_name="John",
            last_name="Doe",
            user_type=User.UserType.TEACHER,
        )
        self.assertEqual(user.username, "user")
        self.assertTrue(user.check_password(self.common_password))
        self.assertEqual(user.email, "a@example.com")
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Doe")
        self.assertEqual(user.user_type, User.UserType.TEACHER)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_with_missing_fields(self):
        user = UserFactory.build(
            username="user",
            password=self.common_password,
            email=None,
            first_name=None,
            last_name=None,
            user_type=None,
        )
        with self.assertRaises(ValidationError) as context:
            user.clean()
        errors = context.exception.error_dict
        self.assertIn("email", errors)
        self.assertIn("first_name", errors)
        self.assertIn("last_name", errors)
        self.assertIn("user_type", errors)

    def test_field_constraints(self):
        username_uniqueness = User._meta.get_field("username").unique
        self.assertTrue(username_uniqueness)
        title_max_length = User._meta.get_field("title").max_length
        self.assertEqual(title_max_length, 10)

    def test_ordering(self):
        self.assertEqual(User._meta.ordering, ["username"])

    def test_user_type_methods(self):
        teacher = UserFactory(user_type=User.UserType.TEACHER)
        self.assertTrue(teacher.is_teacher())
        student = UserFactory(user_type=User.UserType.STUDENT)
        self.assertTrue(student.is_student())

    def test_get_full_name(self):
        user = UserFactory(first_name="John", last_name="Doe", title=User.Title.PROF)
        self.assertEqual(user.get_full_name(), "Prof. John Doe")
        user_no_title = UserFactory(
            first_name="John", last_name="Doe", title=User.Title.PREFER_NOT_TO_SAY
        )
        self.assertEqual(user_no_title.get_full_name(), "John Doe")


class TeacherProfileModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create(username="testusername")
        cls.teacher = TeacherProfileFactory.create(
            user=cls.user, biography="I am a teacher."
        )

    def test_create_teacher_profile(self):
        self.assertEqual(self.teacher.user, self.user)
        self.assertEqual(self.teacher.biography, "I am a teacher.")

    def test_field_constraints(self):
        user_related_name = TeacherProfile._meta.get_field("user")._related_name
        self.assertEqual(user_related_name, "teacher_profile")
        title_max_length = TeacherProfile._meta.get_field("biography").max_length
        self.assertEqual(title_max_length, 500)

    def test_str(self):
        self.assertEqual(str(self.teacher), self.user.username)


class StudentProfileModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create()
        cls.program = ProgramFactory.create()
        cls.student = StudentProfileFactory.create(
            user=cls.user,
            status="Feeling good!",
            program=cls.program,
        )

    def test_create_student_profile(self):
        self.assertEqual(self.student.user, self.user)
        self.assertEqual(self.student.status, "Feeling good!")
        self.assertEqual(self.student.program, self.program)
        expected_expiry_date = self.student.registration_date + relativedelta(years=6)
        self.assertEqual(self.student.registration_expiry_date, expected_expiry_date)

    def test_field_constraints(self):
        user_related_name = StudentProfile._meta.get_field("user")._related_name
        self.assertEqual(user_related_name, "student_profile")
        program_related_name = StudentProfile._meta.get_field("program")._related_name
        self.assertEqual(program_related_name, "students")
        status_max_length = StudentProfile._meta.get_field("status").max_length
        self.assertEqual(status_max_length, 20)
        registration_date_editable = StudentProfile._meta.get_field(
            "registration_date"
        ).editable
        self.assertFalse(registration_date_editable)
        registration_expiry_date_editable = StudentProfile._meta.get_field(
            "registration_expiry_date"
        ).editable
        self.assertFalse(registration_expiry_date_editable)

    def test_str(self):
        self.assertEqual(str(self.student), self.user.username)


class AcademicTermModelTest(TestCase, TermTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.semester_val, cls.year, cls.start, cls.end = get_term_datetimes()
        cls.term = AcademicTermFactory.create(
            semester=AcademicTerm.SemesterType(cls.semester_val),
            year=cls.year,
            start_datetime=cls.start,
            end_datetime=cls.end,
        )
        cls.next_term = cls.create_next_term(cls.term)
        cls.previous_term = cls.create_previous_term(cls.term)

    def test_create_academic_term(self):
        self.assertEqual(
            self.term.semester, AcademicTerm.SemesterType(self.semester_val)
        )
        self.assertEqual(self.term.year, self.year)
        self.assertEqual(self.term.start_datetime, self.start)
        self.assertEqual(self.term.end_datetime, self.end)

    def test_ordering(self):
        self.assertEqual(AcademicTerm._meta.ordering, ["-start_datetime"])

    def test_status_property(self):
        self.assertEqual(self.term.status, AcademicTerm.TermStatus.IN_PROGRESS)
        self.assertEqual(self.previous_term.status, AcademicTerm.TermStatus.ENDED)
        self.assertEqual(self.next_term.status, AcademicTerm.TermStatus.NOT_STARTED)

    def test_clean_method_with_valid_dates(self):
        valid_term = AcademicTermFactory.create()
        try:
            valid_term.clean()
        except ValidationError as e:
            self.fail(f"clean() raised ValidationError unexpectedly. {e}")

    def test_clean_method_with_invalid_dates(self):
        invalid_term = AcademicTermFactory.create()
        invalid_term.start_datetime = invalid_term.end_datetime + relativedelta(days=1)
        with self.assertRaises(ValidationError) as context:
            invalid_term.clean()
        errors = context.exception.error_dict
        self.assertIn("start_datetime", errors)

    def test_str(self):
        start = self.term.start_datetime.strftime("%b %d, %Y")
        end = self.term.end_datetime.strftime("%b %d, %Y")
        self.assertEqual(
            str(self.term),
            f"{self.term.get_semester_display()} {self.term.year} ({start} to {end})",
        )


class CourseModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.course_title = "Math"
        cls.program = ProgramFactory.create()
        cls.teacher = TeacherProfileFactory.create()
        cls.course = CourseFactory.create(
            title=cls.course_title,
            description="Math is fun!",
            program=cls.program,
            teacher=cls.teacher,
        )

    def test_create_course(self):
        self.assertEqual(self.course.title, "Math")
        self.assertEqual(self.course.description, "Math is fun!")
        self.assertEqual(self.course.program, self.program)
        self.assertEqual(self.course.teacher, self.teacher)

    def test_field_constraints(self):
        title_max_length = Course._meta.get_field("title").max_length
        self.assertEqual(title_max_length, 100)
        description_max_length = Course._meta.get_field("description").max_length
        self.assertEqual(description_max_length, 500)
        program_related_name = Course._meta.get_field("program")._related_name
        self.assertEqual(program_related_name, "courses")
        teacher_related_name = Course._meta.get_field("teacher")._related_name
        self.assertEqual(teacher_related_name, "courses")

    def test_ordering(self):
        self.assertEqual(Course._meta.ordering, ["title"])

    def test_unique_together(self):
        with self.assertRaises(IntegrityError):
            CourseFactory.create(title=self.course_title, teacher=self.teacher)

    def test_str(self):
        self.assertEqual(str(self.course), self.course.title)


class CourseOfferingModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.course = CourseFactory.create()
        cls.term = AcademicTermFactory.create()
        cls.offering = CourseOfferingFactory.create(course=cls.course, term=cls.term)

    def test_create_course_offering(self):
        self.assertEqual(self.offering.course, self.course)
        self.assertEqual(self.offering.term, self.term)

    def test_field_constraints(self):
        course_related_name = CourseOffering._meta.get_field("course")._related_name
        self.assertEqual(course_related_name, "offerings")
        term_related_name = CourseOffering._meta.get_field("term")._related_name
        self.assertEqual(term_related_name, "offerings")

    def test_unique_together(self):
        with self.assertRaises(IntegrityError):
            CourseOfferingFactory.create(course=self.course, term=self.term)

    def test_str(self):
        self.assertEqual(str(self.offering), f"{self.course} - {self.term}")


class EnrollmentModelTest(TestCase, TermTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.student = StudentProfileFactory.create()
        cls.offering = CourseOfferingFactory.create()
        cls.enrollment = EnrollmentFactory.create(
            student=cls.student, offering=cls.offering
        )
        cls.next_term = cls.create_next_term(cls.offering.term)
        cls.previous_term = cls.create_previous_term(cls.offering.term)

    def test_create_enrollment(self):
        self.assertEqual(self.enrollment.student, self.student)
        self.assertEqual(self.enrollment.offering, self.offering)
        self.assertEqual(self.enrollment.grade, Enrollment.Grade.NOT_GRADED)

    def test_field_constraints(self):
        student_related_name = Enrollment._meta.get_field("student")._related_name
        self.assertEqual(student_related_name, "enrollments")
        offering_related_name = Enrollment._meta.get_field("offering")._related_name
        self.assertEqual(offering_related_name, "enrollments")
        grade_default = Enrollment._meta.get_field("grade").default
        self.assertEqual(grade_default, Enrollment.Grade.NOT_GRADED)
        enrolled_at_auto_now_add = Enrollment._meta.get_field(
            "enrolled_at"
        ).auto_now_add
        self.assertTrue(enrolled_at_auto_now_add)

    def test_unique_together(self):
        with self.assertRaises(IntegrityError):
            EnrollmentFactory.create(student=self.student, offering=self.offering)

    def test_status_property(self):
        self.assertEqual(self.enrollment.status, "In Progress")
        next_offering = CourseOfferingFactory.create(term=self.next_term)
        next_enrollment = EnrollmentFactory.create(offering=next_offering)
        self.assertEqual(next_enrollment.status, "Registered")
        prev_offering = CourseOfferingFactory.create(term=self.previous_term)
        prev_enrollment = EnrollmentFactory.create(offering=prev_offering)
        self.assertEqual(prev_enrollment.status, "Ended")

    def test_clean_method_with_valid_data(self):
        next_offering = CourseOfferingFactory.create(term=self.next_term)
        student = StudentProfileFactory.create()
        valid_enrollment = EnrollmentFactory.build(
            student=student, offering=next_offering
        )
        try:
            valid_enrollment.clean()
        except ValidationError as e:
            self.fail(f"clean() raised ValidationError unexpectedly. {e}")

    def test_clean_method_with_invalid_data(self):
        invalid_enrollment = EnrollmentFactory.build(
            student=self.student, offering=self.offering
        )
        with self.assertRaises(ValidationError) as context:
            invalid_enrollment.clean()
        errors = context.exception.error_dict
        self.assertIn("offering_started", errors)
        self.assertIn("enrollment_duplicate", errors)

    def test_str(self):
        self.assertEqual(str(self.enrollment), f"{self.student} ({self.offering})")


class FeedbackModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = StudentProfileFactory.create()
        cls.course = CourseFactory.create()
        cls.feedback = FeedbackFactory.create(
            student=cls.student, course=cls.course, comments="This is a test feedback."
        )

    def test_create_feedback(self):
        self.assertEqual(self.feedback.student, self.student)
        self.assertEqual(self.feedback.course, self.course)
        self.assertEqual(self.feedback.comments, "This is a test feedback.")

    def test_field_constraints(self):
        student_related_name = Feedback._meta.get_field("student")._related_name
        self.assertEqual(student_related_name, "feedbacks")
        course_related_name = Feedback._meta.get_field("course")._related_name
        self.assertEqual(course_related_name, "feedbacks")
        comments_max_length = Feedback._meta.get_field("comments").max_length
        self.assertEqual(comments_max_length, 500)
        updated_at_auto_now = Feedback._meta.get_field("updated_at").auto_now
        self.assertTrue(updated_at_auto_now)
        created_at_auto_now_add = Feedback._meta.get_field("created_at").auto_now_add
        self.assertTrue(created_at_auto_now_add)

    def test_unique_together(self):
        with self.assertRaises(IntegrityError):
            FeedbackFactory.create(student=self.student, course=self.course)

    def test_str(self):
        self.assertEqual(str(self.feedback), f"{self.student} ({self.course})")


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class MaterialModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.course = CourseFactory.create()
        cls.material = MaterialFactory.create(
            title="Test Material",
            description="This is a test material.",
            course=cls.course,
        )

    def test_create_material(self):
        self.assertEqual(self.material.title, "Test Material")
        self.assertEqual(self.material.description, "This is a test material.")
        self.assertEqual(self.material.course, self.course)

    def test_field_constraints(self):
        title_max_length = Material._meta.get_field("title").max_length
        self.assertEqual(title_max_length, 100)
        original_filename_max_length = Material._meta.get_field(
            "original_filename"
        ).max_length
        self.assertEqual(original_filename_max_length, 255)
        uploaded_at_auto_now_add = Material._meta.get_field("uploaded_at").auto_now_add
        self.assertTrue(uploaded_at_auto_now_add)
        course_related_name = Material._meta.get_field("course")._related_name
        self.assertEqual(course_related_name, "materials")

    def test_ordering(self):
        self.assertEqual(Material._meta.ordering, ["-uploaded_at"])

    def test_file_upload_and_validation(self):
        file_content = b"Dummy PNG content"
        file = SimpleUploadedFile("test.png", file_content, content_type="image/png")
        material = MaterialFactory.create(course=self.course, file=file)
        self.assertTrue(material.file)
        self.assertEqual(material.original_filename, "test.png")
        self.assertTrue(os.path.exists(material.file.path))
        self.assertIn("materials/", material.file.name)

    def test_valid_file_extension(self):
        for valid_ext in ALLOWED_MATERIAL_EXTENSIONS:
            file = SimpleUploadedFile(
                f"test.{valid_ext}",
                b"Dummy text content",
                content_type="application/octet-stream",
            )
            material = MaterialFactory.build(course=self.course, file=file)
            try:
                material.full_clean()
            except ValidationError as e:
                self.fail(f"full_clean() raised ValidationError unexpectedly. {e}")

    def test_invalid_file_extension(self):
        for invalid_ext in ["txt", "doc", "docx"]:
            file = SimpleUploadedFile(
                f"test.{invalid_ext}",
                b"Dummy text content",
                content_type="application/octet-stream",
            )
            material = MaterialFactory.build(course=self.course, file=file)
            with self.assertRaises(ValidationError) as context:
                material.full_clean()
            errors = context.exception.error_dict
            self.assertIn("file", errors)

    def test_file_size_validator(self):
        large_file = SimpleUploadedFile(
            "large.png", b"0" * (MAX_MATERIAL_FILE_SIZE_BYTES + 1)
        )  # 1MB + 1 byte
        material = MaterialFactory.build(course=self.course, file=large_file)
        with self.assertRaises(ValidationError) as context:
            material.full_clean()
        errors = context.exception.error_dict
        self.assertIn("file", errors)

    def test_str(self):
        self.assertEqual(str(self.material), self.material.title)


class NotificationModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create()
        cls.notification = NotificationFactory.create(
            user=cls.user,
            message="You have a new notification.",
            link_path="/",
            link_text="View materials",
        )

    def test_create_notification(self):
        self.assertEqual(self.notification.user, self.user)
        self.assertEqual(self.notification.message, "You have a new notification.")
        self.assertEqual(self.notification.link_path, "/")
        self.assertEqual(self.notification.link_text, "View materials")

    def test_field_constraints(self):
        user_related_name = Notification._meta.get_field("user")._related_name
        self.assertEqual(user_related_name, "notifications")
        message_max_length = Notification._meta.get_field("message").max_length
        self.assertEqual(message_max_length, 500)
        created_at_auto_now_add = Notification._meta.get_field(
            "created_at"
        ).auto_now_add
        self.assertTrue(created_at_auto_now_add)
        is_read_default = Notification._meta.get_field("is_read").default
        self.assertFalse(is_read_default)

    def test_clean_method_with_valid_data(self):
        course = CourseFactory.create()
        link_path = reverse("material-list", args=[course.id])
        valid_notification = NotificationFactory.build(
            user=self.user,
            link_path=link_path,
            link_text=MATERIAL_CREATED_NOTIFICATION_LINK_TEXT,
        )
        try:
            valid_notification.clean()
        except ValidationError as e:
            self.fail(f"clean() raised ValidationError unexpectedly. {e}")

    def test_clean_method_with_invalid_data(self):
        invalid_notification = NotificationFactory.build(
            user=self.user, link_path="/", link_text=None
        )
        with self.assertRaises(ValidationError) as context:
            invalid_notification.clean()
        errors = context.exception.error_dict
        self.assertIn("link_path", errors)

    def test_ordering(self):
        self.assertEqual(Notification._meta.ordering, ["-created_at"])

    def test_str(self):
        self.assertEqual(
            str(self.notification),
            f"{self.user.username} ({self.notification.message[:20]}...)",
        )


class QASessionModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.course = CourseFactory.create()
        cls.qa_session = QASessionFactory.create(
            course=cls.course,
            room_name="1_20240801000000000000",
        )

    def test_create_qa_session(self):
        self.assertEqual(self.qa_session.course, self.course)
        self.assertEqual(self.qa_session.room_name, "1_20240801000000000000")

    def test_field_constraints(self):
        course_related_name = QASession._meta.get_field("course")._related_name
        self.assertEqual(course_related_name, "qa_session")
        room_name_max_length = QASession._meta.get_field("room_name").max_length
        self.assertEqual(room_name_max_length, 200)
        created_at_auto_now_add = QASession._meta.get_field("created_at").auto_now_add
        self.assertTrue(created_at_auto_now_add)

    def test_status_methods(self):
        self.assertTrue(self.qa_session.is_active())
        self.assertFalse(self.qa_session.is_ended())

    def test_unique_constraint(self):
        with self.assertRaises(IntegrityError):
            QASessionFactory.create(course=self.course)


class QAQuestionModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.qa_question = QAQuestionFactory.create(
            room_name="1_20240801000000000000",
            text="I have a question.",
            sender="John Doe",
            timestamp="2024-08-01 00:00:00+00:00",
        )

    def test_create_qa_question(self):
        self.assertEqual(self.qa_question.room_name, "1_20240801000000000000")
        self.assertEqual(self.qa_question.text, "I have a question.")
        self.assertEqual(self.qa_question.sender, "John Doe")
        self.assertEqual(self.qa_question.timestamp, "2024-08-01 00:00:00+00:00")

    def test_field_constraints(self):
        room_name_max_length = QAQuestion._meta.get_field("room_name").max_length
        self.assertEqual(room_name_max_length, 200)
        sender_max_length = QAQuestion._meta.get_field("sender").max_length
        self.assertEqual(sender_max_length, 310)
        timestamp_auto_now_add = QAQuestion._meta.get_field("timestamp").auto_now_add
        self.assertFalse(timestamp_auto_now_add)

    def test_ordering(self):
        self.assertEqual(QAQuestion._meta.ordering, ["-timestamp"])
