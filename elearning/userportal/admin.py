from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import *
from django.contrib.auth.admin import UserAdmin

PortalUser = get_user_model()


class PortalUserAdmin(UserAdmin):
    additional_fieldsets = (("Portal User Info", {"fields": ("user_type", "title")}),)

    fieldsets = UserAdmin.fieldsets + additional_fieldsets


class StudentProfileAdmin(admin.ModelAdmin):
    readonly_fields = ["registration_expiry_date"]


admin.site.register(PortalUser, PortalUserAdmin)
admin.site.register(Program)
admin.site.register(TeacherProfile)
admin.site.register(StudentProfile, StudentProfileAdmin)
