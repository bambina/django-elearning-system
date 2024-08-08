from datetime import date

from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import *


class StudentForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(help_text="Required.")
    last_name = forms.CharField(help_text="Required.")
    title = forms.ChoiceField(
        choices=PortalUser.Title.choices,
        initial=PortalUser.Title.PREFER_NOT_TO_SAY,
        required=False,
    )

    class Meta:
        model = PortalUser
        fields = (
            "username",
            "password1",
            "password2",
            "email",
            "first_name",
            "last_name",
            "title",
        )


class StudentProfileForm(forms.ModelForm):
    program = forms.ModelChoiceField(
        queryset=Program.objects.all(), help_text="Required."
    )
    registration_date = forms.DateField(initial=date.today, help_text="Required.")

    class Meta:
        model = StudentProfile
        fields = (
            "program",
            "registration_date",
        )
