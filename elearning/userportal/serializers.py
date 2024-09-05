from rest_framework import serializers
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field

from django.db import transaction
from django.contrib.auth import get_user_model

from userportal.models import *


class ProgramSerializer(serializers.ModelSerializer):
    """Serializer for Program model"""

    class Meta:
        model = Program
        fields = ["title", "description"]
        read_only_fields = fields


class TeacherProfileSerializer(serializers.ModelSerializer):
    """Serializer for TeacherProfile model"""

    class Meta:
        model = TeacherProfile
        fields = ["biography"]
        read_only_fields = []

    def update(self, instance, validated_data):
        """Update fields that are not read-only"""
        for attr, value in validated_data.items():
            if attr not in self.Meta.read_only_fields:
                setattr(instance, attr, value)
        instance.save()
        return instance


class StudentProfileSerializer(serializers.ModelSerializer):
    """Serializer for StudentProfile model"""

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
        """Update fields that are not read-only"""
        for attr, value in validated_data.items():
            if attr not in self.Meta.read_only_fields:
                setattr(instance, attr, value)
        instance.save()
        return instance


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with nested profile data.
    Includes TeacherProfile or StudentProfile based on user type.
    """

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
        read_only_fields = ["id", "username", "user_type_display"]

    @extend_schema_field(OpenApiTypes.STR)
    def get_user_type_display(self, obj):
        """Return user type display value"""
        return obj.get_user_type_display() if obj.user_type else None

    def to_representation(self, instance):
        """
        Extend the default serialization by adding a 'profile' field
        containing either TeacherProfile or StudentProfile data, depending on the
        user type.
        """
        ret = super().to_representation(instance)
        if instance.is_teacher():
            ret["profile"] = TeacherProfileSerializer(instance.teacher_profile).data
        elif instance.is_student():
            ret["profile"] = StudentProfileSerializer(instance.student_profile).data
        return ret

    def to_internal_value(self, data):
        """
        Process input data before validation.
        This method extracts the 'profile' data from the input and includes it in the
        internal value dictionary. This allows for handling nested profile data
        during deserialization and update operations.
        """
        internal_value = super().to_internal_value(data)
        profile_data = data.get("profile")
        if profile_data:
            internal_value["profile"] = profile_data
        return internal_value

    def _get_update_profile_serializer(self, instance, data):
        """Return the appropriate profile serializer for update operation."""
        if instance.is_teacher():
            return TeacherProfileSerializer(
                instance.teacher_profile, data=data, partial=True
            )
        elif instance.is_student():
            return StudentProfileSerializer(
                instance.student_profile, data=data, partial=True
            )
        return None

    @transaction.atomic
    def update(self, instance, validated_data):
        """Update User and associated profile data."""
        profile_data = validated_data.pop("profile", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.clean()
        instance.save()
        if profile_data:
            if serializer := self._get_update_profile_serializer(
                instance, profile_data
            ):
                serializer.is_valid(raise_exception=True)
                serializer.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "title",
            "user_type",
        ]
        read_only_fields = ["id", "username", "user_type"]
