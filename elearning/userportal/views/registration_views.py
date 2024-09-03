from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash, login
from django.contrib.auth.forms import PasswordChangeForm
from django.db import transaction
from django.contrib.auth.models import Group

from userportal.models import *
from userportal.forms import *


def signup(request):
    if request.method == "POST":
        student_form = StudentForm(request.POST)
        student_profile_form = StudentProfileForm(request.POST)
        if student_form.is_valid() and student_profile_form.is_valid():
            try:
                with transaction.atomic():
                    student = student_form.save(commit=False)
                    student.save()
                    student_profile = student_profile_form.save(commit=False)
                    student_profile.user = student
                    student_profile.save()
                    # Add student to student permission group
                    student_group = Group.objects.get(name="student")
                    student.groups.add(student_group)
                messages.success(request, CREATE_STUDENT_ACCOUNT_SUCCESS_MSG)
                login(request, student)
                return redirect("home")
            except Exception:
                student_form.add_error(None, ERR_UNEXPECTED_MSG)
    else:
        student_form = StudentForm()
        student_profile_form = StudentProfileForm()

    forms = [student_form, student_profile_form]
    any_non_field_errors = any(form.non_field_errors() for form in forms)
    context = {
        "forms": [student_form, student_profile_form],
        "any_non_field_errors": any_non_field_errors,
    }
    return render(request, "registration/signup.html", context)


@login_required(login_url="login")
def password_change(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            try:
                user = form.save()
                update_session_auth_hash(request, user)
                messages.success(request, PASSWORD_CHANGE_SUCCESS_MSG)
            except Exception:
                form.add_error(None, ERR_UNEXPECTED_MSG)
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "registration/password_change.html", {"form": form})
