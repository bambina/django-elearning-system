from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import *
from django.contrib.auth.admin import UserAdmin
from django import forms

AuthUser = get_user_model()


class AuthUserAdmin(UserAdmin):
    additional_fieldsets = (("Portal User Info", {"fields": ("user_type", "title")}),)

    fieldsets = UserAdmin.fieldsets + additional_fieldsets


class BaseProfileAdminForm(forms.ModelForm):
    INVALID_USER_TYPE_MSG = "Invalid user type for this profile."

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get("user")
        if user and user.user_type != self.EXPECTED_USER_TYPE:
            raise ValidationError(
                {
                    "user": ValidationError(
                        f"{INVALID_VALUE_MSG.format(value=user.user_type)} {self.INVALID_USER_TYPE_MSG}",
                        code=VALIDATION_ERR_INVALID,
                    )
                }
            )
        return cleaned_data


class TeacherProfileAdminForm(BaseProfileAdminForm):
    class Meta:
        model = TeacherProfile
        fields = "__all__"

    EXPECTED_USER_TYPE = AuthUser.UserType.TEACHER
    INVALID_USER_TYPE_MSG = INVALID_TEACHER_PROFILE_USER_TYPE_MSG


class StudentProfileAdminForm(BaseProfileAdminForm):
    class Meta:
        model = StudentProfile
        fields = "__all__"

    EXPECTED_USER_TYPE = AuthUser.UserType.STUDENT
    INVALID_USER_TYPE_MSG = INVALID_STUDENT_PROFILE_USER_TYPE_MSG


class TeacherProfileAdmin(admin.ModelAdmin):
    form = TeacherProfileAdminForm


class StudentProfileAdmin(admin.ModelAdmin):
    readonly_fields = ["registration_expiry_date"]
    form = StudentProfileAdminForm


admin.site.register(AuthUser, AuthUserAdmin)
admin.site.register(Program)
admin.site.register(TeacherProfile, TeacherProfileAdmin)
admin.site.register(StudentProfile, StudentProfileAdmin)
