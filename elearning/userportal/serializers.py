from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = "__all__"
        read_only_fields = ["id", "title", "description"]


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
            "user_type",
            "user_type_display",
        ]
        read_only_fields = ["id", "username", "email", "user_type", "user_type_display"]

    def get_user_type_display(self, obj):
        return obj.get_user_type_display() if obj.user_type else None

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr not in self.Meta.read_only_fields:
                setattr(instance, attr, value)
        instance.save()
        return instance


class TeacherProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = TeacherProfile
        fields = "__all__"
        read_only_fields = ["id"]

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)
        if user_data:
            user_serializer = UserSerializer(
                instance.user, data=user_data, partial=True
            )
            user_serializer.is_valid()
            user_serializer.save()

        return super().update(instance, validated_data)


class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    program = ProgramSerializer()

    class Meta:
        model = StudentProfile
        fields = "__all__"
        read_only_fields = [
            "id",
            "program",
            "registration_date",
            "registration_expiry_date",
        ]

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)
        if user_data:
            user_serializer = UserSerializer(
                instance.user, data=user_data, partial=True
            )
            user_serializer.is_valid()
            user_serializer.save()

        for attr, value in validated_data.items():
            if attr not in self.Meta.read_only_fields:
                setattr(instance, attr, value)
        instance.save()
        return instance
