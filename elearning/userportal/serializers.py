from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = ["title", "description"]
        read_only_fields = fields


class TeacherProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherProfile
        fields = ["biography"]
        read_only_fields = []

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr not in self.Meta.read_only_fields:
                setattr(instance, attr, value)
        instance.save()
        return instance


class StudentProfileSerializer(serializers.ModelSerializer):
    program = ProgramSerializer(required=False)

    class Meta:
        model = StudentProfile
        fields = ["status", "program", "registration_date", "registration_expiry_date"]
        read_only_fields = [
            "program",
            "registration_date",
            "registration_expiry_date",
        ]

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr not in self.Meta.read_only_fields:
                setattr(instance, attr, value)
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    user_type_display = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "title",
            "user_type_display",
        ]
        read_only_fields = ["id", "username", "email", "user_type_display"]

    @extend_schema_field(OpenApiTypes.STR)
    def get_user_type_display(self, obj):
        return obj.get_user_type_display() if obj.user_type else None

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.is_teacher():
            ret["profile"] = TeacherProfileSerializer(instance.teacher_profile).data
        elif instance.is_student():
            ret["profile"] = StudentProfileSerializer(instance.student_profile).data
        return ret

    def to_internal_value(self, data):
        internal_value = super().to_internal_value(data)
        profile = data.pop("profile", None)
        if not profile or not self.instance.user_type:
            return internal_value

        if self.instance.is_teacher():
            profile_serializer = TeacherProfileSerializer(data=profile)
        else:
            profile_serializer = StudentProfileSerializer(data=profile)
        profile_serializer.is_valid(raise_exception=True)
        internal_value["profile"] = profile_serializer.validated_data
        return internal_value

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        profile_data = validated_data.pop("profile", None)
        if profile_data:
            if instance.is_teacher():
                serializer = TeacherProfileSerializer(
                    instance.teacher_profile, data=profile_data, partial=True
                )
            elif instance.is_student():
                serializer = StudentProfileSerializer(
                    instance.student_profile, data=profile_data, partial=True
                )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return instance
