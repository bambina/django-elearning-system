from django.test import Client, TestCase
from django.urls import reverse
from userportal.models import PortalUser

from userportal.constants import *


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = PortalUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
            first_name="Firstname",
            last_name="Lastname",
            user_type=PortalUser.UserType.TEACHER,
        )


class LoginViewTestCase(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url = reverse("login")

    def test_login_view_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login", html=True)

    def test_login_view_post(self):
        response = self.client.post(
            self.url, {"username": "testuser", "password": "testpassword"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_view_post_invalid(self):
        response = self.client.post(
            self.url, {"username": "testuser", "password": "wrongpassword"}
        )
        error_message = "Please enter a correct username and password. Note that both fields may be case-sensitive."
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, error_message, html=True)
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class LogoutViewTestCase(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url = reverse("logout")

    def test_logout_view(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("index"))
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout_view_not_logged_in(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login") + "?next=/logout/")


class PasswordChangeViewTestCase(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url = reverse("password_change")
        cls.new_password = "apple52cat"

    def test_password_change_view_get(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Password change", html=True)

    def test_password_change_view_post(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
            {
                "old_password": "testpassword",
                "new_password1": self.new_password,
                "new_password2": self.new_password,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, PASSWORD_CHANGE_SUCCESS_MSG, html=True)
        self.assertTrue(response.wsgi_request.user.check_password(self.new_password))

    def test_password_change_view_post_invalid_old_password(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
            {
                "old_password": "wrongpassword",
                "new_password1": self.new_password,
                "new_password2": self.new_password,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Your old password was entered incorrectly. Please enter it again.",
            html=True,
        )
        self.assertTrue(response.wsgi_request.user.check_password("testpassword"))

    def test_password_change_view_post_invalid_new_password(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
            {
                "old_password": "testpassword",
                "new_password1": "abc",
                "new_password2": "abc",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "This password is too short. It must contain at least 8 characters.",
            html=True,
        )
        self.assertTrue(response.wsgi_request.user.check_password("testpassword"))
