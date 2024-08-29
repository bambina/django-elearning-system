from django.test import TestCase
from userportal.models import *
from django.contrib.auth import get_user_model
from userportal.tests.model_factories import *
from django.core.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

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
        with self.assertRaises(ValidationError) as context:
            UserFactory.create(
                username="user",
                password=self.common_password,
                email=None,
                first_name=None,
                last_name=None,
                user_type=None,
            )
        errors = context.exception.error_dict
        self.assertIn("email", errors)
        self.assertIn("first_name", errors)
        self.assertIn("last_name", errors)
        self.assertIn("user_type", errors)

    def test_field_constraints(self):
        username_uniqueness = User._meta.get_field("username").unique
        self.assertTrue(username_uniqueness)
        email_uniqueness = User._meta.get_field("email").unique
        self.assertTrue(email_uniqueness)
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
        self.assertEqual(status_max_length, 100)
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
