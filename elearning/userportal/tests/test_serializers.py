from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from userportal.models import *
from userportal.serializers import *
from userportal.tests.model_factories import *

AuthUser = get_user_model()


class ProgramSerializerTest(TestCase):
    def setUp(self):
        self.program = ProgramFactory(
            title="Program Title", description="Program Description"
        )

    def test_serialize_model(self):
        serializer = ProgramSerializer(instance=self.program)
        assert serializer.data == {
            "title": "Program Title",
            "description": "Program Description",
        }

    def test_read_only_fields(self):
        serializer = ProgramSerializer()
        assert serializer.Meta.read_only_fields == ["title", "description"]


class TeacherProfileSerializerTest(TestCase):
    def setUp(self):
        self.teacher = TeacherProfileFactory(biography="Teacher Biography")

    def test_serialize_model(self):
        serializer = TeacherProfileSerializer(instance=self.teacher)
        assert serializer.data == {"biography": self.teacher.biography}

    def test_read_only_fields(self):
        serializer = TeacherProfileSerializer()
        assert serializer.Meta.read_only_fields == []

    def test_update(self):
        serializer = TeacherProfileSerializer()
        updated_teacher = serializer.update(
            self.teacher, {"biography": "Updated Biography"}
        )
        assert updated_teacher.biography == "Updated Biography"


class StudentProfileSerializerTest(TestCase):
    def setUp(self):
        self.program = ProgramFactory()
        self.student = StudentProfileFactory(
            status="Student Status",
            program=self.program,
            registration_date="",
            registration_expiry_date=timezone.now(),
        )

    def test_serialize_model(self):
        serializer = StudentProfileSerializer(instance=self.student)
        assert serializer.data == {
            "status": self.student.status,
            "program": ProgramSerializer(instance=self.program).data,
            "registration_date": self.student.registration_date.isoformat(),
            "registration_expiry_date": self.student.registration_expiry_date.isoformat(),
        }

    def test_read_only_fields(self):
        serializer = StudentProfileSerializer()
        assert serializer.Meta.read_only_fields == [
            "program",
            "registration_date",
            "registration_expiry_date",
        ]

    def test_update(self):
        serializer = StudentProfileSerializer()
        updated_student = serializer.update(self.student, {"status": "Updated Status"})
        assert updated_student.status == "Updated Status"


class UserProfileSerializerTest(TestCase):
    def setUp(self):
        self.teacher_user = UserFactory(
            user_type=AuthUser.UserType.TEACHER,
            username="teacher1",
            email="t1@example.com",
            first_name="Teacher",
            last_name="User",
            title=AuthUser.Title.PROF,
        )
        self.teacher_profile = TeacherProfileFactory(
            user=self.teacher_user, biography="Teacher Biography"
        )

    def test_serialize_teacher(self):
        serializer = UserProfileSerializer(instance=self.teacher_user)
        assert serializer.data == {
            "id": self.teacher_user.id,
            "username": self.teacher_user.username,
            "email": self.teacher_user.email,
            "first_name": self.teacher_user.first_name,
            "last_name": self.teacher_user.last_name,
            "title": self.teacher_user.title,
            "user_type_display": "Teacher",
            "profile": TeacherProfileSerializer(instance=self.teacher_profile).data,
        }

    def test_update_teacher(self):
        serializer = UserProfileSerializer()
        updated_teacher = serializer.update(
            self.teacher_user, {"first_name": "Updated First Name"}
        )
        assert updated_teacher.first_name == "Updated First Name"

    def test_update_teacher_with_invalid_data(self):
        serializer = UserProfileSerializer()
        invalid_data = {
            "first_name": "",
            "last_name": "",
            "email": "",
        }
        with self.assertRaises(ValidationError) as context:
            serializer.update(self.teacher_user, invalid_data)
        errors = context.exception.error_dict
        self.assertIn("first_name", errors)
        self.assertIn("last_name", errors)
        self.assertIn("email", errors)


class UserSerializerTest(TestCase):
    def setUp(self):
        self.student_user = UserFactory(
            user_type=AuthUser.UserType.STUDENT,
        )

    def test_serialize_student(self):
        serializer = UserSerializer(instance=self.student_user)
        assert serializer.data == {
            "id": self.student_user.id,
            "username": self.student_user.username,
            "email": self.student_user.email,
            "first_name": self.student_user.first_name,
            "last_name": self.student_user.last_name,
            "title": self.student_user.title,
            "user_type": self.student_user.user_type,
        }
