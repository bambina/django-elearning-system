from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash, login
from django.contrib.auth.forms import PasswordChangeForm

from userportal.models import *
from userportal.forms import *


def signup(request):
    if request.method == "POST":
        student_form = StudentForm(request.POST)
        student_profile_form = StudentProfileForm(request.POST)
        if student_form.is_valid() and student_profile_form.is_valid():
            student = student_form.save(commit=False)
            student.user_type = PortalUser.UserType.STUDENT
            student.save()
            student_profile = student_profile_form.save(commit=False)
            student_profile.user = student
            student_profile.save()
            messages.success(request, CREATE_STUDENT_ACCOUNT_SUCCESS_MSG)
            login(request, student)
            return redirect("home")
    else:
        student_form = StudentForm()
        student_profile_form = StudentProfileForm()

    context = {
        "student_form": student_form,
        "student_profile_form": student_profile_form,
    }
    return render(request, "registration/signup.html", context)


@login_required(login_url="login")
def password_change(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, PASSWORD_CHANGE_SUCCESS_MSG)
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "registration/password_change.html", {"form": form})
