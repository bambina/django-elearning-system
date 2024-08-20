from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from django.shortcuts import get_object_or_404


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_teacher():
            teacher_profile = get_object_or_404(
                TeacherProfile.objects.select_related("user"), user=request.user
            )
            serializer = TeacherProfileSerializer(teacher_profile)
        elif request.user.is_student():
            student_profile = get_object_or_404(
                StudentProfile.objects.select_related("user"), user=request.user
            )
            serializer = StudentProfileSerializer(student_profile)
        else:
            user = get_object_or_404(get_user_model(), pk=request.user.pk)
            serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request):
        if request.user.is_teacher():
            profile = get_object_or_404(
                TeacherProfile.objects.select_related("user"), user=request.user
            )
            serializer = TeacherProfileSerializer(
                profile, data=request.data, partial=True
            )
        elif request.user.is_student():
            profile = get_object_or_404(
                StudentProfile.objects.select_related("user"), user=request.user
            )
            serializer = StudentProfileSerializer(
                profile, data=request.data, partial=True
            )
        else:
            user = get_object_or_404(get_user_model(), pk=request.user.pk)
            serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
