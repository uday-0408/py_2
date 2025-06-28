from django.shortcuts import get_object_or_404, render
from App.code_runner2 import execute_code
from rest_framework import generics
from .models import Problem, TestCase
from .serializers import ProblemSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from datetime import timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.db import IntegrityError
from django.contrib import messages
from .models import AppUser
from App.code_runner3 import execute_code as execute_code3

# from django.contrib.auth import get_user_model


# username:uday password:1996


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data["token"])
        return Response(
            {
                "token": token.key,
                "user_id": token.user_id,
                "username": token.user.username,
            }
        )


# ✅ Login View (sets token as cookie)
class CookieLoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data["token"])

        res = Response({"message": "Login successful"}, status=status.HTTP_200_OK)
        res.set_cookie(
            key="auth_token",
            value=token.key,
            httponly=True,
            secure=False,  # Set to True for production
            samesite="Lax",
            max_age=86400,  # 1 day
        )
        return res


# ✅ Logout View (deletes cookie)
@api_view(["POST"])
def logout_view(request):
    response = Response({"message": "Logged out successfully"})
    response.delete_cookie("auth_token")
    return response


# ✅ Protected View (requires valid token in cookie)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def secret_view(request):
    return Response({"data": f"Hello {request.user.username}"})


class ProblemListAPIView(generics.ListAPIView):
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer


class ProblemDetailAPIView(generics.RetrieveAPIView):
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer
    lookup_field = "slug"


def home_page(request):
    return render(request, "home.html")


def problem_list(request):
    problems = Problem.objects.all()
    return render(request, "problems.html", {"problems": problems})


language_id_map2 = {"python": "python", "c": "c", "cpp": "cpp", "java": "java"}


def compile_code_monaco2(request, slug=None):
    problem = None
    if slug:
        try:
            problem = get_object_or_404(Problem, slug=slug)
        except:
            problem = None

    if request.method == "POST":
        code = request.POST.get("code", "")
        language = request.POST.get("language", "python")
        input_data = request.POST.get("input", "")  # optional input field

        if not code.strip():
            return render(
                request,
                "monaco_unified.html",
                {"error": "No code submitted.", "problem": problem},
            )

        language_mapped = language_id_map2.get(language.lower(), "python")

        output = execute_code3(code, language=language_mapped, input_data=input_data)

        return render(
            request,
            "monaco_unified.html",
            {
                "code": code,
                "language": language,
                "input": input_data,
                "output": output,
                "problem": problem,
            },
        )

    return render(request, "monaco_unified.html", {"problem": problem})


# perfect
def compile_code_monaco1(request, slug=None):
    problem = None
    if slug:
        problem = get_object_or_404(Problem, slug=slug)

    if request.method == "POST":
        code = request.POST.get("code", "")
        language = request.POST.get("language", "python")

        if not code.strip():
            return render(
                request,
                "monaco_unified.html",
                {"error": "No code submitted.", "problem": problem},
            )

        output = execute_code(
            code, language_id=language_id_map2.get(language, "python")
        )

        return render(
            request,
            "monaco_unified.html",
            {"code": code, "language": language, "output": output, "problem": problem},
        )

    return render(request, "monaco_unified.html", {"problem": problem})


from django.shortcuts import render, get_object_or_404
from App.models import Problem
from .utils import generate_default_function, generate_runner_code, compare_outputs
from .code_runner2 import execute_code  # Your function to call Judge0 or similar API


def compile_code_monaco1(request, slug=None):
    problem = get_object_or_404(Problem, slug=slug) if slug else None

    if problem:
        starter_code = generate_default_function(problem)
    else:
        starter_code = "# Write your code here\nprint('Hello World')"

    if request.method == "POST":
        code = request.POST.get("code", "")
        language = request.POST.get("language", "python")
        action = request.POST.get("action")

        if not code.strip():
            return render(
                request,
                "monaco_unified.html",
                {
                    "error": "No code submitted.",
                    "problem": problem,
                    "code": starter_code,
                },
            )

        runner_code, cases = generate_runner_code(problem, mode=action)
        final_code = code + runner_code
        print(final_code)
        raw_output = execute_code(final_code, language_id=71)  # default Python
        results, all_passed, failed_case_number = compare_outputs(raw_output, cases)

        if action == "run":
            return render(
                request,
                "monaco_unified.html",
                {
                    "code": code,
                    "language": language,
                    "run_results": results,
                    "problem": problem,
                    "action": "run",
                },
            )

        elif action == "submit":
            return render(
                request,
                "monaco_unified.html",
                {
                    "code": code,
                    "language": language,
                    "problem": problem,
                    "action": "submit",
                    "all_passed": all_passed,
                    "total_cases": len(results),
                    "passed_cases": sum(1 for r in results if r["passed"]),
                    "failed_case_number": failed_case_number,
                },
            )

    return render(
        request,
        "monaco_unified.html",
        {"code": starter_code, "problem": problem, "language": "python"},
    )


from .utils import generate_runner_code, generate_default_function

from django.shortcuts import render, get_object_or_404
from .models import Problem
from App.code_runner3 import execute_code as execute_code3  # your FastAPI caller

language_map = {
    "python": "python",
    "c": "c",
    "cpp": "cpp",
    "java": "java",
}


def compile_code_monaco(request, slug=None):
    problem = get_object_or_404(Problem, slug=slug) if slug else None

    # Starter code
    starter_code = (
        "# Write your code here\nprint('Hello World')"
        if not problem
        else "# TODO: fetch or generate starter code from problem if needed"
    )

    if request.method == "POST":
        code = request.POST.get("code", "")
        language = request.POST.get("language", "python")
        action = request.POST.get("action", "run")
        language = language_map.get(language.lower(), "python")

        if not code.strip():
            return render(
                request,
                "monaco_unified.html",
                {
                    "error": "No code submitted.",
                    "problem": problem,
                    "code": starter_code,
                },
            )

        # 🎯 Run Mode: just run with sample input (user can add input box if needed)
        if action == "run":
            sample_input = request.POST.get("input", "")
            output = execute_code3(code, language=language, input_data=sample_input)
            print(f"output:{output}")
            return render(
                request,
                "monaco_unified.html",
                {
                    "code": code,
                    "language": language,
                    "output": output,
                    "problem": problem,
                    "action": "run",
                },
            )

        # ✅ Submit Mode: run through all test cases in the DB
        elif action == "submit" and problem:
            test_cases = problem.test_cases.all()  # assuming FK relation `test_cases`
            results = []
            passed_cases = 0
            for i, case in enumerate(test_cases, start=1):
                result = execute_code(
                    code, language=language, input_data=case.input_data
                )
                passed = result.strip() == case.expected_output.strip()
                # print(f"result: " + result)
                results.append(
                    {
                        "input": case.input_data,
                        "expected": case.expected_output,
                        "output": result.strip(),
                        "passed": passed,
                        "case_number": i,
                    }
                )
                if passed:
                    passed_cases += 1
                else:
                    break  # stop at first failure

            all_passed = passed_cases == len(test_cases)

            return render(
                request,
                "monaco_unified.html",
                {
                    "code": code,
                    "language": language,
                    "problem": problem,
                    "action": "submit",
                    "all_passed": all_passed,
                    "total_cases": len(test_cases),
                    "passed_cases": passed_cases,
                    "failed_case_number": passed_cases + 1 if not all_passed else None,
                    "run_results": results,
                },
            )

    return render(
        request,
        "monaco_unified.html",
        {
            "code": starter_code,
            "problem": problem,
            "language": "python",
        },
    )


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

        # ✅ Check for uniqueness
        if AppUser.objects.filter(email=email).exists():
            return render(request, "register.html", {"error": "Email already exists"})

        if AppUser.objects.filter(phone=phone).exists():
            return render(
                request, "register.html", {"error": "Phone number already exists"}
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
            )
            user.save()
            messages.success(request, "Registration successful.")
            return redirect("login")

        except IntegrityError as e:
            print(f"IntegrityError: {e}")
            return render(request, "register.html", {"error": "Something went wrong"})

    return render(request, "register.html")


def execution_result(request):
    return render(request, "output.html")


def languages_supported(request):
    return render(request, "languages.html")


def about_page(request):
    return render(request, "about.html")


def contact_page(request):
    return render(request, "contact.html")


def user_history(request):
    return render(request, "history.html")


# Language map
language_id_map = {
    "python": 71,
    "cpp": 54,
    "java": 62,
    "javascript": 63,
}
