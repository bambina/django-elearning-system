from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

from userportal.models import *
from userportal.constants import *
from userportal.tests.model_factories import *

AuthUser = get_user_model()


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.teacher_user = UserFactory.create(
            username="testuser",
            password="testpassword",
            user_type=AuthUser.UserType.TEACHER,
        )
        cls.teacher_profile = TeacherProfileFactory.create(
            user=cls.teacher_user,
            biography="Prof. Firstname Lastname is a Professor of Computer Science at the University of California.",
        )
        cls.student_user = UserFactory.create(
            user_type=AuthUser.UserType.STUDENT,
        )
        cls.student_profile = StudentProfileFactory.create(user=cls.student_user)
        cls.teacher_group = Group.objects.get(name=PERMISSION_GROUP_TEACHER)
        cls.teacher_user.groups.add(cls.teacher_group)
        cls.student_group = Group.objects.get(name=PERMISSION_GROUP_STUDENT)
        cls.student_user.groups.add(cls.student_group)
        cls.course = CourseFactory.create(
            title="Data Science", teacher=cls.teacher_profile
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
        self.client.force_login(self.teacher_user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("swagger-ui"))
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout_view_not_logged_in(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login") + "?next=/logout/")


class PasswordChangeViewTestCase(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url = reverse("password-change")
        cls.new_password = "apple52cat"

    def test_password_change_view_get(self):
        self.client.force_login(self.teacher_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Password change", html=True)

    def test_password_change_view_post(self):
        self.client.force_login(self.teacher_user)
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
        self.client.force_login(self.teacher_user)
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
        self.client.force_login(self.teacher_user)
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


class SignUpViewTestCase(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url = reverse("signup")
        cls.program = ProgramFactory.create(title="Program 1")
        cls.new_student_data = {
            "username": "new-student",
            "email": "stu@example.com",
            "password1": "crispy123student",
            "password2": "crispy123student",
            "first_name": "New",
            "last_name": "Student",
            "user_type": AuthUser.UserType.STUDENT,
            "program": cls.program.id,
        }

    def test_signup_view_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Register", html=True)

    def test_signup_view_post(self):
        response = self.client.post(self.url, self.new_student_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertTrue(response.wsgi_request.user.is_student())
        self.assertEqual(
            response.wsgi_request.user.student_profile.program, self.program
        )

    def test_signup_view_post_invalid(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.", html=True)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertFalse(AuthUser.objects.filter(username="new-student").exists())


class CourseOfferingListViewTestCase(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.offering = CourseOfferingFactory.create(course=cls.course)
        cls.url = reverse("offering-list", args=[cls.course.id])

    def test_course_offering_list_view_get(self):
        self.client.force_login(self.teacher_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Course Offerings", html=True)
        self.assertContains(response, self.offering.term.status.label, html=True)

    def test_course_offering_list_view_get_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse("login") + f"?next=/courses/{self.course.id}/offerings/"
        )

    def test_course_offering_list_view_get_student(self):
        self.client.force_login(self.student_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertContains(
            response, "Permission Denied (403)", status_code=403, html=True
        )
