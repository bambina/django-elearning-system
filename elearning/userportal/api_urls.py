from django.urls import path
from userportal.apis import *

urlpatterns = [
    # API Views
    # Token Authentication
    path("api-token-auth/", CustomObtainAuthToken.as_view(), name="api_token_auth"),
    # User Profile
    path("users/me/", UserProfileView.as_view(), name="user-profile"),
    # User List
    path("users/", UserListView.as_view(), name="user-list"),
]
