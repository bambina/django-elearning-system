from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import *
from django.contrib.auth.admin import UserAdmin
from django import forms

PortalUser = get_user_model()


class PortalUserAdmin(UserAdmin):
    additional_fieldsets = (("Portal User Info", {"fields": ("user_type", "title")}),)

    fieldsets = UserAdmin.fieldsets + additional_fieldsets


class TeacherProfileAdminForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get("user")
        if user and user.user_type != PortalUser.UserType.TEACHER:
            raise ValidationError(
                {
                    "user": ValidationError(
                        f"{INVALID_VALUE_MSG.format(value=user.user_type)} {INVALID_TEACHER_PROFILE_USER_TYPE_MSG}",
                        code=VALIDATION_ERR_INVALID,
                    )
                }
            )
        return cleaned_data


class TeacherProfileAdmin(admin.ModelAdmin):
    form = TeacherProfileAdminForm


class StudentProfileAdminForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get("user")
        if user and user.user_type != PortalUser.UserType.STUDENT:
            raise ValidationError(
                {
                    "user": ValidationError(
                        f"{INVALID_VALUE_MSG.format(value=user.user_type)} {INVALID_STUDENT_PROFILE_USER_TYPE_MSG}",
                        code=VALIDATION_ERR_INVALID,
                    )
                }
            )
        return cleaned_data


class StudentProfileAdmin(admin.ModelAdmin):
    readonly_fields = ["registration_expiry_date"]
    form = StudentProfileAdminForm


admin.site.register(PortalUser, PortalUserAdmin)
admin.site.register(Program)
admin.site.register(TeacherProfile, TeacherProfileAdmin)
admin.site.register(StudentProfile, StudentProfileAdmin)
