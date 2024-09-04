from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path("", main_views.index, name="index"),
    path("home/", main_views.home, name="home"),
    path(
        "notifications/",
        main_views.NotificationListView.as_view(),
        name="notification-list",
    ),
    path("signup/", registration_views.signup, name="signup"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path(
        "logout/",
        login_required(login_url="login")(auth_views.LogoutView.as_view()),
        name="logout",
    ),
    path(
        "password-change/", registration_views.password_change, name="password-change"
    ),
    path("users/", user_views.UserListView.as_view(), name="user-list"),
    path(
        "users/<str:username>/", user_views.UserDetailView.as_view(), name="user-detail"
    ),
    path(
        "users/<str:username>/<str:activate>/",
        user_views.toggle_active_status,
        name="user-toggle-active-status",
    ),
    path("courses/", course_views.CourseListView.as_view(), name="course-list"),
    path(
        "courses/<int:pk>/",
        course_views.CourseDetailView.as_view(),
        name="course-detail",
    ),
    path(
        "courses/create/", course_views.CourseCreateView.as_view(), name="course-create"
    ),
    path(
        "courses/<int:course_id>/offerings/",
        course_offering_views.CourseOfferingListView.as_view(),
        name="offering-list",
    ),
    path(
        "courses/<int:course_id>/offerings/create/",
        course_offering_views.create_course_offering,
        name="offering-create",
    ),
    path(
        "courses/<int:course_id>/offerings/<int:offering_id>/enroll/",
        course_offering_views.EnrollCourseView.as_view(),
        name="course-enroll",
    ),
    path(
        "courses/<int:course_id>/offerings/<int:offering_id>/enrolled-students/",
        course_offering_views.EnrolledStudentListView.as_view(),
        name="enrolled-student-list",
    ),
    path(
        "courses/<int:course_id>/feedback/create/",
        feedback_views.FeedbackCreateView.as_view(),
        name="feedback-create",
    ),
    path(
        "courses/<int:course_id>/feedback/",
        feedback_views.FeedbackListView.as_view(),
        name="feedback-list",
    ),
    path(
        "courses/<int:course_id>/materials/",
        course_views.MaterialListView.as_view(),
        name="material-list",
    ),
    path(
        "courses/<int:course_id>/materials/create/",
        course_views.CreateMaterialView.as_view(),
        name="material-create",
    ),
    path(
        "courses/<int:course_id>/materials/<int:material_id>/download/",
        course_views.download_material,
        name="material-download",
    ),
    path(
        "courses/<int:course_id>/start-qa-session/",
        course_views.start_qa_session,
        name="start-qa-session",
    ),
    path(
        "courses/<int:course_id>/end-qa-session/",
        course_views.end_qa_session,
        name="end-qa-session",
    ),
    path(
        "courses/<int:course_id>/qa-session/",
        course_views.QASessionView.as_view(),
        name="qa-session",
    ),
]
