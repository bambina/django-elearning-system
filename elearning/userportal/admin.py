from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import *

PortalUser = get_user_model()


class StudentProfileAdmin(admin.ModelAdmin):
    readonly_fields = ["registration_expiry_date"]


admin.site.register(PortalUser)
admin.site.register(Program)
admin.site.register(TeacherProfile)
admin.site.register(StudentProfile, StudentProfileAdmin)
