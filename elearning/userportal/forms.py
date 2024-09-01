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

    class Meta:
        model = StudentProfile
        fields = ("program",)


class UserSearchForm(forms.Form):
    keywords = forms.CharField(
        required=False,
        label="Keywords",
        widget=forms.TextInput(attrs={"placeholder": "Enter username, etc."}),
    )
    user_type = forms.MultipleChoiceField(
        choices=PortalUser.UserType.choices,
        required=False,
        label="User Type",
        widget=forms.CheckboxSelectMultiple,
    )


class CourseSearchForm(forms.Form):
    keywords = forms.CharField(
        required=False,
        label="Keywords",
        widget=forms.TextInput(attrs={"placeholder": "Enter course title, etc."}),
    )


class StatusForm(forms.Form):
    status = forms.CharField(
        required=False,
        max_length=20,
        widget=forms.TextInput(
            attrs={"placeholder": "What's your status?", "class": "form-control"}
        ),
    )


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["title", "description", "program"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control"}),
            "program": forms.Select(attrs={"class": "form-control"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title")
        program = cleaned_data.get("program")
        if title and program:
            # Check if the course already exists for the selected program
            if Course.objects.filter(title=title, program=program).exists():
                raise ValidationError(
                    f"The course '{title}' already exists for the selected program."
                )
        return cleaned_data


class CourseOfferingForm(forms.ModelForm):
    class Meta:
        model = CourseOffering
        fields = ["term"]
        widgets = {
            "term": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        self.course = kwargs.pop("course", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        term = cleaned_data.get("term")
        if self.course and term:
            # Check if the course offering already exists for the selected term
            if CourseOffering.objects.filter(course=self.course, term=term).exists():
                raise ValidationError(
                    "This course offering already exists for the selected term."
                )

        return cleaned_data


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ["comments"]
        widgets = {
            "comments": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "How well did the course content meet your learning expectations?",
                    "rows": 5,
                }
            ),
        }


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ["title", "description", "file"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter a brief description of the file.",
                    "rows": 5,
                }
            ),
            "file": forms.FileInput(attrs={"class": "form-control"}),
        }
