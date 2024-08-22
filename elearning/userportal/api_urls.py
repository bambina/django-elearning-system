from django.urls import path
from .apis import *
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="api:schema"),
        name="swagger-ui",
    ),
    path(
        "schema/redoc/",
        SpectacularRedocView.as_view(url_name="api:schema"),
        name="redoc",
    ),
    path("api-token-auth/", CustomObtainAuthToken.as_view(), name="api_token_auth"),
    path("users/me/", UserProfileView.as_view(), name="user-profile"),
    path("users/", UserListView.as_view(), name="user-list"),
]
