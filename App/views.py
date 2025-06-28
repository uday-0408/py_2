# Django imports
from django.shortcuts import render, get_object_or_404, redirect
from django.db import IntegrityError
from django.contrib.auth.hashers import make_password

# REST framework imports
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

# App-specific models and serializers
from .models import Problem, StarterCode, TestCase, AppUser
from .serializers import ProblemSerializer

# Code execution engines
from App.code_runner3 import execute_code  # Your FastAPI caller

# from App.code_runner2 import execute_code as execute_code2  # Uncomment if needed

# Utility functions
from .utils import generate_runner_code, generate_default_function

# Standard library
import json
import textwrap
from django.contrib import messages


# username:uday password:1996


# ✅ Login View (sets token in cookie)
class CookieLoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        # Authenticates user and generates token
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data["token"])

        # Sets token in HTTP-only cookie
        res = Response({"message": "Login successful"}, status=status.HTTP_200_OK)
        res.set_cookie(
            key="auth_token",
            value=token.key,
            httponly=True,
            secure=False,  # Change to True in production (HTTPS)
            samesite="Lax",
            max_age=86400,  # 1 day
        )
        return res


# ✅ Logout View (clears cookie)
@api_view(["POST"])
def logout_view(request):
    response = Response({"message": "Logged out successfully"})
    response.delete_cookie("auth_token")
    return response


# ✅ Protected View (requires valid token from cookie)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def secret_view(request):
    return Response({"data": f"Hello, {request.user.username}!"})


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


# language_id_map2 = {"python": "python", "c": "c", "cpp": "cpp", "java": "java"}

language_map = {
    "python": "python",
    "c": "c",
    "cpp": "cpp",
    "java": "java",
}

# from code_runner3 import execute_code

# Mapping from POST language key to internal language identifier
language_map = {
    "python": "python",
    "cpp": "cpp",
    "java": "java",
    "javascript": "js",
}

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import json


@csrf_exempt
def compile_code_basic(request):
    """
    Handles code execution without a problem object.
    Renders monaco_unified.html with code, input, and output.
    """
    if request.method == "POST":
        code = request.POST.get("code", "").strip()
        language_key = request.POST.get("language", "python").lower()
        custom_input = request.POST.get("input", "")

        language = language_map.get(language_key, "python")

        if not code:
            return render(
                request,
                "monaco_unified.html",
                {
                    "error": "No code submitted.",
                    "code": "",
                    "language": language,
                    "input": custom_input,
                    "output": "",
                },
            )

        print(f"[INFO] Running code in {language} with custom input.")
        result = execute_code(code, language=language, input_data=custom_input)

        return render(
            request,
            "monaco_unified.html",
            {
                "code": code,
                "language": language,
                "input": custom_input,
                "output": result.strip(),
                "action": "run",
            },
        )

    # For GET requests, just show an empty editor
    return render(
        request,
        "monaco_unified.html",
        {
            "code": "# Write your code here\nprint('Hello World')",
            "language": "python",
            "input": "",
            "output": "",
        },
    )


def get_starter_code(problem, language):
    slug = getattr(problem, "slug", "fallback_function")
    print(f"[DEBUG] Fetching starter code for problem: {slug}, language: {language}")

    if not problem:
        print("[WARN] No problem provided, using default fallback starter code.")
        return {
            "python": f"def {slug}(input_data):\n    # Write your code here\n    pass",
            "java": f"public class Solution {{\n    public Object {slug}(String input) {{\n        // Write your code here\n        return null;\n    }}\n}}",
            "cpp": f'#include <string>\nusing namespace std;\n\nstring {slug}(string input) {{\n    // Write your code here\n    return "";\n}}',
            "js": f'function {slug}(input) {{\n    // Write your code here\n    return "";\n}}',
        }.get(language, "// Language not supported.")

    try:
        code = problem.starter_code.get_code(language, slug=slug)
        if not code or not code.strip():
            print("[WARN] Starter code is empty, falling back.")
            raise ValueError("Empty code")
        return code
    except (StarterCode.DoesNotExist, ValueError):
        print("[INFO] Returning fallback starter code.")
        return {
            "python": f"def {slug}(input_data):\n    # Write your code here\n    pass",
            "java": f"public class Solution {{\n    public Object {slug}(String input) {{\n        // Write your code here\n        return null;\n    }}\n}}",
            "cpp": f'#include <string>\nusing namespace std;\n\nstring {slug}(string input) {{\n    // Write your code here\n    return "";\n}}',
            "js": f'function {slug}(input) {{\n    // Write your code here\n    return "";\n}}',
        }.get(language, "// Language not supported.")


import json
import textwrap

import re


def extract_python_function_name(code, fallback="function_name"):
    """Extracts the function name from a Python code snippet."""
    match = re.search(r"def\s+(\w+)\s*\(", code)
    return match.group(1) if match else fallback


def run_examples(problem, code, language):
    if not problem:
        print("[WARN] No problem provided to run_examples.")
        return []

    print(f"[DEBUG] Running examples for problem: {problem.slug}, language: {language}")
    examples = getattr(problem, "examples_group", None)
    examples = examples.examples if examples else []

    # Extract structured inputs and expected outputs
    inputs = [ex.get("input") for ex in examples if ex.get("input") is not None]
    expected_outputs = [
        ex.get("output") for ex in examples if ex.get("output") is not None
    ]

    results = []
    starter_code = problem.starter_code.get_code("python", slug=problem.slug)
    func_name = extract_python_function_name(
        starter_code, fallback=problem.slug.replace("-", "_")
    )

    # ----------------------
    # DRIVER CODE GENERATION
    # ----------------------
    if language == "python":
        driver_code = f"""
import json

def run_all():
    inputs = {json.dumps(inputs)}
    results = []

    for test in inputs:
        try:
            args = [test[str(i)] for i in range(1, len(test) + 1)]
            result = {func_name}(*args)
        except Exception as e:
            result = str(e)
        results.append(result)

    print(json.dumps(results))

if __name__ == "__main__":
    run_all()
"""
    else:
        print("[WARN] Unsupported language in run_examples.")
        return []

    # Combine user's code with driver code
    final_code = code.strip() + "\n\n" + textwrap.dedent(driver_code)

    # Execute and capture result
    result = execute_code(final_code, language=language, input_data="")
    print("[DEBUG] Raw result from execution:", result)

    # Parse output from the final printed line
    try:
        output_line = result.strip().splitlines()[-1]
        actual_outputs = json.loads(output_line)
    except Exception as e:
        print("[ERROR] Failed to parse output:", e)
        actual_outputs = []

    # Construct result list
    for i, (raw_input, expected_output) in enumerate(
        zip(inputs, expected_outputs), start=1
    ):
        output_val = actual_outputs[i - 1] if i - 1 < len(actual_outputs) else "Error"
        results.append(
            {
                "input": raw_input,
                "expected": (
                    expected_output.strip()
                    if isinstance(expected_output, str)
                    else expected_output
                ),
                "output": (
                    output_val.strip() if isinstance(output_val, str) else output_val
                ),
                "passed": (
                    output_val.strip() == expected_output.strip()
                    if isinstance(expected_output, str) and isinstance(output_val, str)
                    else output_val == expected_output
                ),
                "case_number": i,
            }
        )

    return results


import json
import textwrap


def submit_test_cases(problem, code, language):
    if not problem:
        print("[WARN] No problem provided to submit_test_cases.")
        return [], 0, 0

    print(f"[DEBUG] Submitting test cases for: {problem.slug}, language: {language}")
    test_cases_group = getattr(problem, "testcase_group", None)
    test_cases = test_cases_group.test_cases if test_cases_group else []

    # Structured input format assumed: {"1": [...], "2": ...}
    inputs = [
        case.get("input_data")
        for case in test_cases
        if case.get("input_data") is not None
    ]
    expected_outputs = [
        case.get("output_data")
        for case in test_cases
        if case.get("output_data") is not None
    ]

    results, passed_cases = [], 0
    starter_code = problem.starter_code.get_code("python", slug=problem.slug)
    func_name = extract_python_function_name(
        starter_code, fallback=problem.slug.replace("-", "_")
    )

    # ----------------------
    # DRIVER CODE GENERATION
    # ----------------------
    if language == "python":
        driver_code = f"""
import json

def run_all():
    inputs = {json.dumps(inputs)}
    results = []

    for test in inputs:
        try:
            args = [test[str(i)] for i in range(1, len(test) + 1)]
            result = {func_name}(*args)
        except Exception as e:
            result = str(e)
        results.append(result)

    print(json.dumps(results))

if __name__ == "__main__":
    run_all()
"""
    else:
        print("[WARN] Unsupported language in submit_test_cases.")
        return [], 0, len(test_cases)

    final_code = code.strip() + "\n\n" + textwrap.dedent(driver_code)

    result = execute_code(final_code, language=language, input_data="")
    print("[DEBUG] Raw test case output:", result)

    try:
        output_line = result.strip().splitlines()[-1]
        actual_outputs = json.loads(output_line)
    except Exception as e:
        print("[ERROR] Could not parse result output:", e)
        actual_outputs = []

    # Match actual and expected output
    for i, (raw_input, expected_output) in enumerate(
        zip(inputs, expected_outputs), start=1
    ):
        output_val = actual_outputs[i - 1] if i - 1 < len(actual_outputs) else "Error"
        output_str = output_val.strip() if isinstance(output_val, str) else output_val
        expected_str = (
            expected_output.strip()
            if isinstance(expected_output, str)
            else expected_output
        )
        passed = output_str == expected_str

        results.append(
            {
                "input": raw_input,
                "expected": expected_str,
                "output": output_str,
                "passed": passed,
                "case_number": i,
            }
        )

        if passed:
            passed_cases += 1
        else:
            break  # Stop on first failed test case (like LeetCode)

    return results, passed_cases, len(test_cases)


def compile_code_monaco(request, slug=None):
    """
    Handles GET and POST requests for code editor interface.
    Returns problem, starter code, test case results, and language info to template.
    """
    print("[INFO] compile_code_monaco view called")
    problem = get_object_or_404(Problem, slug=slug) if slug else None
    lang = request.POST.get("language", "python").lower()
    language = language_map.get(lang, "python")
    print(f"[DEBUG] Selected language: {language}")

    starter_code = (
        get_starter_code(problem, language)
        if problem
        else "# Write your code here\nprint('Hello World')"
    )

    # Preload starter code for all languages
    starter_codes = {}
    for lang_key, lang_name in language_map.items():
        starter_codes[lang_key] = (
            get_starter_code(problem, lang_name) if problem else ""
        )

    if request.method == "POST":
        print("[INFO] Handling POST request")
        code = request.POST.get("code", "")
        action = request.POST.get("action", "run")

        if not code.strip():
            print("[WARN] No code submitted")
            return render(
                request,
                "monaco_unified.html",
                {
                    "error": "No code submitted.",
                    "problem": problem,
                    "code": starter_code,
                    "language": language,
                    "starter_codes": starter_codes,
                },
            )

        if action == "run":
            print("[INFO] Action: run")
            results = run_examples(problem, code.strip(), language)
            return render(
                request,
                "monaco_unified.html",
                {
                    "code": code,
                    "language": language,
                    "problem": problem,
                    "action": "run",
                    "run_results": results,
                    "starter_codes": starter_codes,
                },
            )

        elif action == "submit":
            print("[INFO] Action: submit")
            results, passed_cases, total_cases = submit_test_cases(
                problem, code.strip(), language
            )
            all_passed = passed_cases == total_cases
            return render(
                request,
                "monaco_unified.html",
                {
                    "code": code,
                    "language": language,
                    "problem": problem,
                    "action": "submit",
                    "all_passed": all_passed,
                    "total_cases": total_cases,
                    "passed_cases": passed_cases,
                    "failed_case_number": passed_cases + 1 if not all_passed else None,
                    "run_results": results,
                    "starter_codes": starter_codes,
                },
            )

    # Handle initial GET request
    print("[INFO] Handling GET request")
    return render(
        request,
        "monaco_unified.html",
        {
            "code": starter_code,
            "problem": problem,
            "language": "python",
            "starter_codes": starter_codes,
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
                # ✅ hash password before saving
                password=make_password(password),
            )
            user.save()
            messages.success(request, "Registration successful.")
            return redirect("auth-page")

        except IntegrityError as e:
            print(f"IntegrityError: {e}")
            return render(request, "auth.html", {"error": "Something went wrong"})

    return render(request, "auth.html")


from django.contrib.auth.hashers import check_password


def login_user(request):
    if request.method == "POST":
        email = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        try:
            user = AppUser.objects.get(email=email)
            if check_password(password, user.password):
                # You can manually store session or return token/cookie
                request.session["user_id"] = user.id
                return redirect("home")
            else:
                return render(request, "auth.html", {"error": "Invalid credentials"})

        except AppUser.DoesNotExist:
            return render(request, "auth.html", {"error": "User not found"})

    return redirect("auth-page")


def auth_view(request):
    return render(request, "auth.html")


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
