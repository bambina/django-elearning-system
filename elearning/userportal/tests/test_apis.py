from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from userportal.tests.model_factories import *
from userportal.serializers import *


# CustomObtainAuthToken
# /api/v1/api-token-auth/	userportal.apis.CustomObtainAuthToken	api:api_token_auth
class CustomObtainAuthTokenTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("api:api_token_auth")
        cls.student = UserFactory.create(
            user_type=AuthUser.UserType.STUDENT, username="A", password="abc"
        )
        cls.teacher = UserFactory.create(
            user_type=AuthUser.UserType.TEACHER, username="B", password="abc"
        )

    def test_obtain_auth_token_valid_student(self):
        """Test that a valid student can obtain an authentication token."""
        data = {"username": self.student.username, "password": "abc"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_obtain_auth_token_valid_teacher(self):
        """Test that a valid teacher can obtain an authentication token."""
        data = {"username": self.teacher.username, "password": "abc"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_obtain_auth_token_invalid(self):
        """Test that an invalid user cannot obtain an authentication token."""
        data = {"username": "invalid", "password": "invalid"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# UserProfileView
# /api/v1/users/me/	userportal.apis.UserProfileView	api:user-profile
class UserProfileViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("api:user-profile")
        cls.student = UserFactory.create(user_type=AuthUser.UserType.STUDENT)
        cls.student_profile = StudentProfileFactory.create(user=cls.student)
        cls.teacher = UserFactory.create(user_type=AuthUser.UserType.TEACHER)
        cls.teacher_profile = TeacherProfileFactory.create(user=cls.teacher)
        cls.email_user = UserFactory.create(email="taken@example.com")

    def test_user_profile_unauthorized(self):
        """Test that unauthenticated users cannot access the user profile."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_profile_student(self):
        """Test that students can access their own user profile."""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {
            "id": self.student.pk,
            "username": self.student.username,
            "email": self.student.email,
            "first_name": self.student.first_name,
            "last_name": self.student.last_name,
            "title": self.student.title,
            "user_type_display": self.student.get_user_type_display(),
            "profile": {
                "status": self.student_profile.status,
                "program": {
                    "title": self.student_profile.program.title,
                    "description": self.student_profile.program.description,
                },
                "registration_date": self.student_profile.registration_date.isoformat(),
                "registration_expiry_date": self.student_profile.registration_expiry_date.isoformat(),
            },
        }
        self.assertEqual(response.data["username"], self.student.username)
        self.assertEqual(response.data, expected_data)

    def test_user_profile_teacher(self):
        """Test that teachers can access their own user profile."""
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {
            "id": self.teacher.pk,
            "username": self.teacher.username,
            "email": self.teacher.email,
            "first_name": self.teacher.first_name,
            "last_name": self.teacher.last_name,
            "title": self.teacher.title,
            "user_type_display": self.teacher.get_user_type_display(),
            "profile": {
                "biography": self.teacher_profile.biography,
            },
        }
        assert response.data == expected_data

    def test_user_profile_update_student(self):
        """Test that students can update their own user profile."""
        self.client.force_authenticate(user=self.student)
        data = {
            "email": "new_email@example.com",
            "first_name": "New",
            "last_name": "Name",
            "profile": {
                "status": "new status",
            },
        }
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student.refresh_from_db()
        self.student_profile.refresh_from_db()
        self.assertEqual(self.student.email, "new_email@example.com")
        self.assertEqual(self.student.first_name, "New")
        self.assertEqual(self.student.last_name, "Name")
        self.assertEqual(self.student_profile.status, "new status")

    def test_user_profile_update_with_invalid_data(self):
        """Test that invalid data cannot be used to update the user profile."""
        self.client.force_authenticate(user=self.student)
        data = {
            "email": "",
            "first_name": "",
            "last_name": "",
        }
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.student.refresh_from_db()
        self.student_profile.refresh_from_db()
        self.assertNotEqual(self.student.email, "")
        self.assertNotEqual(self.student.first_name, "")
        self.assertNotEqual(self.student.last_name, "")

    def test_user_profile_update_with_invalid_email(self):
        """Test that an email address that is already in use cannot be used to update the user profile."""
        self.client.force_authenticate(user=self.student)
        data = {
            "email": "taken@example.com",
        }
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data["detail"])
        self.student.refresh_from_db()
        self.assertNotEqual(self.student.email, "taken@example.com")


# UserListView
# /api/v1/users/	userportal.apis.UserListView	api:user-list
class UserListTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("api:user-list")
        cls.student = UserFactory.create(
            user_type=AuthUser.UserType.STUDENT, username="A"
        )
        cls.teacher = UserFactory.create(
            user_type=AuthUser.UserType.TEACHER, username="B"
        )
        cls.admin = UserFactory.create(
            is_staff=True
        )  # Not included in the API response

    def test_user_list_unauthorized(self):
        """Test that unauthenticated users cannot access the user list."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_list_forbidden_for_students(self):
        """Test that students cannot access the user list."""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_list_accessible_by_teacher(self):
        """
        Test that teachers can access the user list.
        """
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = [
            {
                "id": self.student.pk,
                "username": self.student.username,
                "email": self.student.email,
                "first_name": self.student.first_name,
                "last_name": self.student.last_name,
                "title": self.student.title,
                "user_type": self.student.user_type,
            },
            {
                "id": self.teacher.pk,
                "username": self.teacher.username,
                "email": self.teacher.email,
                "first_name": self.teacher.first_name,
                "last_name": self.teacher.last_name,
                "title": self.teacher.title,
                "user_type": self.teacher.user_type,
            },
        ]
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(response.data["results"], expected_data)

    def test_user_list_accessible_by_admin(self):
        """
        Test that admins can access the user list.
        """
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
