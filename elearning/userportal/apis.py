from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from django.shortcuts import get_object_or_404
from rest_framework.generics import GenericAPIView
from drf_spectacular.utils import extend_schema
from .api_examples import *


class UserProfileView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return get_object_or_404(get_user_model(), pk=self.request.user.pk)

    def get(self, request):
        serializer = self.get_serializer(self.get_object())
        return Response(serializer.data)

    @extend_schema(request=UserSerializer, examples=[teacher_example, student_example])
    def put(self, request):
        serializer = self.get_serializer(
            self.get_object(), data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
