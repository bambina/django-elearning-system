from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path("", views.index, name="index"),
    path("signup/", views.signup, name="signup"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path(
        "logout/",
        login_required(login_url="login")(auth_views.LogoutView.as_view()),
        name="logout",
    ),
    path("password-change/", views.password_change, name="password-change"),
    path("home/", views.home, name="home"),
    path("users/", views.UserListView.as_view(), name="user-list"),
    path("users/<str:username>/", views.UserDetailView.as_view(), name="user-detail"),
    path("courses/", views.CourseListView.as_view(), name="course-list"),
    path("courses/<int:pk>/", views.CourseDetailView.as_view(), name="course-detail"),
    path("courses/create/", views.create_course, name="course-create"),
    path(
        "courses/<int:course_id>/offerings/",
        views.CourseOfferingListView.as_view(),
        name="offering-list",
    ),
    path(
        "courses/<int:course_id>/offerings/create/",
        views.create_course_offering,
        name="offering-create",
    ),
    path(
        "courses/<int:course_id>/offerings/<int:offering_id>/enroll/",
        views.enroll_course,
        name="enroll-course",
    ),
]
