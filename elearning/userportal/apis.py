from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from django.shortcuts import get_object_or_404
from rest_framework.generics import GenericAPIView
from drf_spectacular.utils import extend_schema
from .api_examples import *
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import ListAPIView
from userportal.api_permissions import IsTeacherGroupOrAdminUser
from django.contrib.auth import get_user_model
from .filters import UserFilter


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
    pass


class UserProfileView(GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return get_object_or_404(get_user_model(), pk=self.request.user.pk)

    def get(self, request):
        serializer = self.get_serializer(self.get_object())
        return Response(serializer.data)

    @extend_schema(
        request=UserSerializer,
        examples=[admin_example, teacher_example, student_example],
    )
    def put(self, request):
        serializer = self.get_serializer(
            self.get_object(), data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(ListAPIView):
    queryset = get_user_model().objects.filter(is_staff=False, is_superuser=False)
    serializer_class = UserSerializer
    permission_classes = [IsTeacherGroupOrAdminUser]
    filterset_class = UserFilter
