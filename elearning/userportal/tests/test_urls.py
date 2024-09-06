from django.test import TestCase
from django.urls import reverse, resolve
from userportal.views import *
from userportal.apis import *

class AdminUrlsTestCase(TestCase):
    # /admin/	django.contrib.admin.sites.index	admin:index
    def test_admin_index_url(self):
        url = reverse('admin:index')
        self.assertEqual(url, '/admin/')
        resolver = resolve('/admin/')
        self.assertEqual(resolver.app_name, 'admin')
        self.assertEqual(resolver.namespace, 'admin')
        self.assertEqual(resolver.view_name, 'admin:index')

class APIUrlsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.namespace = 'api'
        cls.app_name = 'userportal'

    # /api/v1/api-token-auth/	userportal.apis.CustomObtainAuthToken	api:api_token_auth
    def test_api_token_auth_url(self):
        url = reverse('api:api_token_auth')
        self.assertTrue(url.startswith('/api/v1/api-token-auth/'))
        resolver = resolve(url)
        self.assertEqual(resolver.namespace, self.namespace)
        self.assertEqual(resolver.app_name, self.app_name)
        self.assertEqual(resolver.func.cls, CustomObtainAuthToken)

class UserPortalAppUrlsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.namespace = ''
        cls.app_name = ''

    # /	drf_spectacular.views.SpectacularSwaggerView	swagger-ui
    def test_swagger_ui_url(self):
        url = reverse('swagger-ui')
        self.assertEqual(url, '/')
        resolver = resolve('/')
        self.assertEqual(resolver.namespace, self.namespace)
        self.assertEqual(resolver.app_name, self.app_name)
        self.assertEqual(resolver.view_name, 'swagger-ui')

    # /home/	userportal.views.main_views.home	home
    def test_userportal_home_url(self):
        url = reverse('home')
        self.assertTrue(url.startswith('/home/'))
        resolver = resolve(url)
        self.assertEqual(resolver.namespace, self.namespace)
        self.assertEqual(resolver.app_name, self.app_name)
        self.assertEqual(resolver.view_name, 'home') 


# /api/v1/schema/	drf_spectacular.views.SpectacularAPIView	api:schema
# /api/v1/schema/redoc/	drf_spectacular.views.SpectacularRedocView	api:redoc
# /api/v1/schema/swagger-ui/	drf_spectacular.views.SpectacularSwaggerView	api:swagger-ui
# /api/v1/users/	userportal.apis.UserListView	api:user-list
# /api/v1/users/me/	userportal.apis.UserProfileView	api:user-profile

# /courses/	userportal.views.course_views.CourseListView	course-list
# /courses/<int:course_id>/end-qa-session/	userportal.views.course_views.end_qa_session	end-qa-session
# /courses/<int:course_id>/feedback/	userportal.views.feedback_views.FeedbackListView	feedback-list
# /courses/<int:course_id>/feedback/create/	userportal.views.feedback_views.FeedbackCreateViewfeedback-create
# /courses/<int:course_id>/materials/	userportal.views.course_views.MaterialListView	material-list
# /courses/<int:course_id>/materials/<int:material_id>/download/	userportal.views.course_views.download_material	material-download
# /courses/<int:course_id>/materials/create/	userportal.views.course_views.CreateMaterialView	material-create
# /courses/<int:course_id>/offerings/	userportal.views.course_offering_views.CourseOfferingListView	offering-list
# /courses/<int:course_id>/offerings/<int:offering_id>/enroll/	userportal.views.course_offering_views.EnrollCourseView	course-enroll
# /courses/<int:course_id>/offerings/<int:offering_id>/enrolled-students/	userportal.views.course_offering_views.EnrolledStudentListView	enrolled-student-list
# /courses/<int:course_id>/offerings/create/	userportal.views.course_offering_views.create_course_offering	offering-create
# /courses/<int:course_id>/qa-session/	userportal.views.course_views.QASessionView	qa-session
# /courses/<int:course_id>/start-qa-session/	userportal.views.course_views.start_qa_session	start-qa-session
# /courses/<int:pk>/	userportal.views.course_views.CourseDetailView	course-detail
# /courses/create/	userportal.views.course_views.CourseCreateView	course-create

# /login/	django.contrib.auth.views.LoginView	login
# /logout/	django.contrib.auth.views.LogoutView	logout
# /notifications/	userportal.views.main_views.NotificationListView	notification-list
# /password-change/	userportal.views.registration_views.password_change	password-change
# /signup/	userportal.views.registration_views.signup	signup
# /users/	userportal.views.user_views.UserListView	user-list
# /users/<str:username>/	userportal.views.user_views.UserDetailView	user-detail
# /users/<str:username>/<str:activate>/	userportal.views.user_views.toggle_active_status	user-toggle-active-status        

