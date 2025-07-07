# auth_views.py

# Django & REST imports
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.db import IntegrityError

from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import logout

# App-specific
from App.models import AppUser


# ------------------------
# ✅ Login via Auth Token (Cookie-based)
# ------------------------
class CookieLoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data["token"])

        res = Response({"message": "Login successful"}, status=status.HTTP_200_OK)
        res.set_cookie(
            key="auth_token",
            value=token.key,
            httponly=True,
            secure=False,  # Use True in production
            samesite="Lax",
            max_age=86400,
        )
        return res


# ------------------------
# ✅ Logout
# ------------------------
def logout_view(request):
    logout(request)  # ✅ removes request.user and clears session
    response = redirect("auth-page")
    return response


# ------------------------
# ✅ View requiring authentication (cookie token)
# ------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def secret_view(request):
    return Response({"data": f"Hello, {request.user.username}!"})


# ------------------------
# ✅ Register User
# ------------------------
def register_user(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        gender = request.POST.get("gender", "").strip()
        dob = request.POST.get("dob", "").strip()
        password = request.POST.get("password", "").strip()

        if AppUser.objects.filter(email=email).exists():
            return render(request, "auth.html", {"error": "Email already exists"})

        if AppUser.objects.filter(phone=phone).exists():
            return render(
                request, "auth.html", {"error": "Phone number already exists"}
            )

        try:
            user = AppUser(
                email=email,
                phone=phone,
                username=username,
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                dob=dob if dob else None,
                password=make_password(password),
            )
            user.save()
            messages.success(request, "Registration successful.")
            return redirect("auth-page")
        except IntegrityError as e:
            print(f"IntegrityError: {e}")
            return render(request, "auth.html", {"error": "Something went wrong"})

    return render(request, "auth.html")


# ------------------------
# ✅ Login (session-based fallback)
# ------------------------
from django.contrib.auth import login  # Add this import
from django.utils.http import url_has_allowed_host_and_scheme


def login_user(request):
    if request.method == "POST":
        email = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        try:
            user = AppUser.objects.get(email=email)
            if check_password(password, user.password):
                login(request, user)  # ✅ This is the key fix

                # ✅ Redirect back to `next` page if present
                next_url = request.GET.get("next") or request.POST.get("next")
                if next_url and url_has_allowed_host_and_scheme(
                    next_url, {request.get_host()}
                ):
                    return redirect(next_url)

                return redirect("home")  # Default fallback
            else:
                return render(request, "auth.html", {"error": "Invalid credentials"})
        except AppUser.DoesNotExist:
            return render(request, "auth.html", {"error": "User not found"})

    return redirect("auth-page")


# ------------------------
# ✅ Render Auth Page
# ------------------------
def auth_view(request):
    return render(request, "auth.html")
