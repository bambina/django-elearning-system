from django.urls import path
from .apis import UserProfileView

urlpatterns = [
    path("users/me/", UserProfileView.as_view(), name="user-profile"),
]
