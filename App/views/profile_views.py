# profile_views.py

from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from .code_views import (
    compile_code_basic,
    compile_code_monaco,
    run_examples,
    submit_test_cases,
)
from App.mongo import get_user_submissions

from django.contrib.auth.decorators import login_required
from App.models import AppUser


# ----------------------------
# ✅ Profile View (GET user data)
# ----------------------------


@login_required(login_url="auth-page")
def profile_view(request):
    user = request.user  # ✅ Use Django auth system
    return render(request, "profile.html", {"user": user})


# ----------------------------
# ✅ Profile Update
# ----------------------------
@login_required(login_url="auth-page")
def update_profile(request):
    user = request.user

    if request.method == "POST":
        user.username = request.POST.get("username", user.username)
        user.email = request.POST.get("email", user.email)
        user.phone = request.POST.get("phone", user.phone)
        user.gender = request.POST.get("gender", user.gender)
        # user.bio = request.POST.get("bio", user.bio)

        dob_input = request.POST.get("dob", "")
        user.dob = dob_input if dob_input else None  # ✅ Set None if empty string

        if "profile_pic" in request.FILES:
            user.profile_pic = request.FILES["profile_pic"]

        user.save()
        return redirect("profile-page")

    return render(request, "update_profile.html", {"user": user})


# ----------------------------
# ✅ General Static Pages
# ----------------------------
def home_page(request):
    return render(request, "home.html")


def problem_list(request):
    from App.models import Problem

    problems = Problem.objects.all()
    return render(request, "problems.html", {"problems": problems})


def execution_result(request):
    return render(request, "output.html")


def languages_supported(request):
    return render(request, "languages.html")


def about_page(request):
    return render(request, "about.html")


def contact_page(request):
    return render(request, "contact.html")


@login_required(login_url="auth-page")
def user_history(request):
    user_id = request.user.id
    submissions = get_user_submissions(user_id)
    return render(request, "history.html", {"submissions": submissions})
