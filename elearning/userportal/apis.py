from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin

from drf_spectacular.utils import extend_schema

from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from userportal.serializers import *
from userportal.api_examples import *
from userportal.filters import UserFilter
from userportal.api_permissions import IsTeacherGroupOrAdminUser


@extend_schema(
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "password": {"type": "string"},
            },
            "required": ["username", "password"],
        }
    },
    responses={200: {"type": "object", "properties": {"token": {"type": "string"}}}},
    methods=["POST"],
    examples=[auth_example],
)
class CustomObtainAuthToken(ObtainAuthToken):
    """
    Custom authentication token endpoint.
    This view extends the default ObtainAuthToken view to provide enhanced
    API documentation.
    """

    pass


class UserProfileView(GenericAPIView, RetrieveModelMixin, UpdateModelMixin):
    """
    API view for retrieving and updating user profiles.
    Requires token authentication.
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        """Get the user object for the current user."""
        return get_object_or_404(get_user_model(), pk=self.request.user.pk)

    def get(self, request, *args, **kwargs):
        """Retrieve the user and profile data for the user."""
        return self.retrieve(request, *args, **kwargs)

    @extend_schema(
        request=UserProfileSerializer,
        examples=[teacher_example, student_example, admin_example],
    )
    def put(self, request, *args, **kwargs):
        """Update the user and profile data."""
        try:
            return self.update(request, *args, **kwargs, partial=True)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserListView(ListAPIView):
    """
    API endpoint that provides a list of non-staff and non-superuser users.
    Requires token authentication. Only accessible to teachers and admins.
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsTeacherGroupOrAdminUser]
    queryset = get_user_model().objects.filter(is_staff=False, is_superuser=False)
    serializer_class = UserSerializer
    filterset_class = UserFilter
