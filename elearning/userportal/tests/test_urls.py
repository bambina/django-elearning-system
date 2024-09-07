from drf_spectacular.views import SpectacularSwaggerView

from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth.views import LoginView, LogoutView

from userportal.views import *
from userportal.apis import UserListView as ApiUserListView
from userportal.apis import CustomObtainAuthToken, UserProfileView


class URLTestBase(TestCase):
    """Base class for URL testing."""

    @classmethod
    def setUpTestData(cls):
        # Override these in the child classes
        cls.namespace = "default_namespace"
        cls.app_name = "default_app_name"

    def verifyURLConfiguration(
        self,
        url_name,
        expected_url,
        expected_class=None,
        expected_func_name: str = None,
        kwargs=None,
    ):
        """Get the URL from the URL name and verify its configuration."""
        url = reverse(url_name, kwargs=kwargs)
        self.assertTrue(url.startswith(expected_url))
        resolver = resolve(url)
        self.assertEqual(resolver.namespace, self.namespace)
        self.assertEqual(resolver.app_name, self.app_name)
        if expected_class:
            self.assertEqual(resolver.func.view_class, expected_class)
        if expected_func_name:
            self.assertEqual(resolver.func.__name__, expected_func_name)
        if kwargs:
            self.assertDictEqual(resolver.kwargs, kwargs)


class AdminUrlsTestCase(URLTestBase):
    """Tests for admin URLs."""

    @classmethod
    def setUpTestData(cls):
        cls.namespace = "admin"
        cls.app_name = "admin"

    # /admin/	django.contrib.admin.sites.index	admin:index
    def test_admin_index_url(self):
        self.verifyURLConfiguration(
            "admin:index", "/admin/", expected_func_name="index"
        )


class APIUrlsTestCase(URLTestBase):
    """Tests for API URLs."""

    @classmethod
    def setUpTestData(cls):
        cls.namespace = "api"
        cls.app_name = "userportal"

    # /api/v1/api-token-auth/	userportal.apis.CustomObtainAuthToken	api:api_token_auth
    def test_api_token_auth_url(self):
        self.verifyURLConfiguration(
            "api:api_token_auth",
            "/api/v1/api-token-auth/",
            expected_class=CustomObtainAuthToken,
        )

    # /api/v1/users/	userportal.apis.UserListView	api:user-list
    def test_api_user_list_url(self):
        self.verifyURLConfiguration(
            "api:user-list", "/api/v1/users/", expected_class=ApiUserListView
        )

    # /api/v1/users/me/	userportal.apis.UserProfileView	api:user-profile
    def test_api_user_profile_url(self):
        self.verifyURLConfiguration(
            "api:user-profile", "/api/v1/users/me/", expected_class=UserProfileView
        )


class UserPortalAppUrlsTestCase(URLTestBase):
    """Tests for User Portal App URLs."""

    @classmethod
    def setUpTestData(cls):
        cls.namespace = ""
        cls.app_name = ""

    # /	drf_spectacular.views.SpectacularSwaggerView	swagger-ui
    def test_swagger_ui_url(self):
        self.verifyURLConfiguration(
            "swagger-ui", "/", expected_class=SpectacularSwaggerView
        )

    # /home/	userportal.views.main_views.home	home
    def test_userportal_home_url(self):
        self.verifyURLConfiguration("home", "/home/", expected_func_name="home")

    # /notifications/	userportal.views.main_views.NotificationListView	notification-list
    def test_notification_list_url(self):
        self.verifyURLConfiguration(
            "notification-list", "/notifications/", expected_class=NotificationListView
        )

    # /login/	django.contrib.auth.views.LoginView	login
    def test_login_url(self):
        self.verifyURLConfiguration("login", "/login/", expected_class=LoginView)

    # /logout/	django.contrib.auth.views.LogoutView	logout
    def test_logout_url(self):
        self.verifyURLConfiguration("logout", "/logout/", expected_class=LogoutView)

    # /password-change/	userportal.views.registration_views.password_change	password-change
    def test_password_change_url(self):
        self.verifyURLConfiguration(
            "password-change",
            "/password-change/",
            expected_func_name="password_change",
        )

    # /signup/	userportal.views.registration_views.signup	signup
    def test_signup_url(self):
        self.verifyURLConfiguration("signup", "/signup/", expected_func_name="signup")

    # /users/	userportal.views.user_views.UserListView	user-list
    def test_user_list_url(self):
        self.verifyURLConfiguration("user-list", "/users/", expected_class=UserListView)

    # /users/<str:username>/	userportal.views.user_views.UserDetailView	user-detail
    def test_user_detail_url(self):
        username = "testuser"
        self.verifyURLConfiguration(
            "user-detail",
            f"/users/{username}/",
            expected_class=UserDetailView,
            kwargs={"username": username},
        )

    # /users/<str:username>/<str:activate>/	userportal.views.user_views.toggle_active_status	user-toggle-active-status
    def test_user_toggle_active_status_url(self):
        username = "testuser"
        activate = "true"
        self.verifyURLConfiguration(
            "user-toggle-active-status",
            f"/users/{username}/{activate}/",
            expected_func_name="toggle_active_status",
            kwargs={"username": username, "activate": activate},
        )

    # /courses/	userportal.views.course_views.CourseListView	course-list
    def test_course_list_url(self):
        self.verifyURLConfiguration(
            "course-list", "/courses/", expected_class=CourseListView
        )

    # /courses/<int:pk>/	userportal.views.course_views.CourseDetailView	course-detail
    def test_course_detail_url(self):
        course_id = 1
        self.verifyURLConfiguration(
            "course-detail",
            f"/courses/{course_id}/",
            expected_class=CourseDetailView,
            kwargs={"pk": course_id},
        )

    # /courses/create/	userportal.views.course_views.CourseCreateView	course-create
    def test_course_create_url(self):
        self.verifyURLConfiguration(
            "course-create", "/courses/create/", expected_class=CourseCreateView
        )

    # /courses/<int:course_id>/offerings/	userportal.views.course_offering_views.CourseOfferingListView	offering-list
    def test_offering_list_url(self):
        course_id = 1
        self.verifyURLConfiguration(
            "offering-list",
            f"/courses/{course_id}/offerings/",
            expected_class=CourseOfferingListView,
            kwargs={"course_id": course_id},
        )

    # /courses/<int:course_id>/offerings/<int:offering_id>/enroll/	userportal.views.course_offering_views.EnrollCourseView	course-enroll
    def test_course_enroll_url(self):
        course_id = 1
        offering_id = 1
        self.verifyURLConfiguration(
            "course-enroll",
            f"/courses/{course_id}/offerings/{offering_id}/enroll/",
            expected_class=EnrollCourseView,
            kwargs={"course_id": course_id, "offering_id": offering_id},
        )

    # /courses/<int:course_id>/offerings/<int:offering_id>/enrolled-students/	userportal.views.course_offering_views.EnrolledStudentListView	enrolled-student-list
    def test_enrolled_student_list_url(self):
        course_id = 1
        offering_id = 1
        self.verifyURLConfiguration(
            "enrolled-student-list",
            f"/courses/{course_id}/offerings/{offering_id}/enrolled-students/",
            expected_class=EnrolledStudentListView,
            kwargs={"course_id": course_id, "offering_id": offering_id},
        )

    # /courses/<int:course_id>/offerings/create/	userportal.views.course_offering_views.create_course_offering	offering-create
    def test_offering_create_url(self):
        course_id = 1
        self.verifyURLConfiguration(
            "offering-create",
            f"/courses/{course_id}/offerings/create/",
            expected_func_name="create_course_offering",
            kwargs={"course_id": course_id},
        )


# /courses/<int:course_id>/feedback/	userportal.views.feedback_views.FeedbackListView	feedback-list
# /courses/<int:course_id>/feedback/create/	userportal.views.feedback_views.FeedbackCreateViewfeedback-create

# /courses/<int:course_id>/materials/	userportal.views.course_views.MaterialListView	material-list
# /courses/<int:course_id>/materials/<int:material_id>/download/	userportal.views.course_views.download_material	material-download
# /courses/<int:course_id>/materials/create/	userportal.views.course_views.CreateMaterialView	material-create

# /courses/<int:course_id>/qa-session/	userportal.views.course_views.QASessionView	qa-session
# /courses/<int:course_id>/start-qa-session/	userportal.views.course_views.start_qa_session	start-qa-session
# /courses/<int:course_id>/end-qa-session/	userportal.views.course_views.end_qa_session	end-qa-session
