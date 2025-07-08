# code_views.py

# Django imports
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

# REST Framework imports
from rest_framework import generics
from App.serializers import ProblemSerializer

# Core models and execution
from App.models import Problem
from App.code_runner.code_runner3 import execute_code
from App.mongo import log_submission_attempt, get_comments_for_problem, save_comment

# Standard library
import json, re, textwrap, time


# ------------------------
# ✅ Language Map
# ------------------------
language_map = {
    "python": "python",
    "cpp": "cpp",
    "java": "java",
    "javascript": "js",
}


# ------------------------
# ✅ Problem APIs
# ------------------------
class ProblemListAPIView(generics.ListAPIView):
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer


class ProblemDetailAPIView(generics.RetrieveAPIView):
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer
    lookup_field = "slug"


# ------------------------
# ✅ Monaco Editor Code Compilation
# ------------------------
def compile_code_monaco(request, slug=None):
    print("[INFO] compile_code_monaco view called")
    problem = get_object_or_404(Problem, slug=slug) if slug else None
    lang = request.POST.get("language", "python").lower()
    language = language_map.get(lang, "python")

    starter_code = (
        get_starter_code(problem, language)
        if problem
        else "# Write your code here\nprint('Hello World')"
    )

    starter_codes = {}
    for lang_key, lang_name in language_map.items():
        starter_codes[lang_key] = (
            get_starter_code(problem, lang_name) if problem else ""
        )

    comments = get_comments_for_problem(slug) if problem else []

    if request.method == "POST":
        code = request.POST.get("code", "").strip()
        action = request.POST.get("action", "run")

        if not request.user.is_authenticated:
            return render(
                request,
                "monaco_unified.html",
                {
                    "error": "⚠️ You must be logged in to run or submit code.",
                    "problem": problem,
                    "code": code or starter_code,
                    "language": language,
                    "starter_codes": starter_codes,
                    "not_logged_in": True,
                    "comments": comments,
                },
            )

        if not code.strip():
            return render(
                request,
                "monaco_unified.html",
                {
                    "error": "No code submitted.",
                    "problem": problem,
                    "code": starter_code,
                    "language": language,
                    "starter_codes": starter_codes,
                    "comments": comments,
                },
            )

        if action == "run":
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
                    "comments": comments,
                },
            )

        elif action == "submit":
            results, passed_cases, total_cases = submit_test_cases(
                problem,
                code.strip(),
                language,
                request.user.id if request.user.is_authenticated else None,
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
                    "comments": comments,
                },
            )

    return render(
        request,
        "monaco_unified.html",
        {
            "code": starter_code,
            "problem": problem,
            "language": "python",
            "starter_codes": starter_codes,
            "comments": comments,
        },
    )


# ------------------------
# ✅ Basic Code Runner (no problem)
# ------------------------
@csrf_exempt
def compile_code_basic(request):
    print("from new Views folder")
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


# ------------------------
# ✅ Utility: Starter Code Loader
# ------------------------
def get_starter_code(problem, language):
    slug = getattr(problem, "slug", "fallback_function")

    try:
        code = problem.starter_code.get_code(language, slug=slug)
        if not code or not code.strip():
            raise ValueError("Empty code")
        return code
    except:
        return {
            "python": f"def {slug}(input_data):\n    # Write your code here\n    pass",
            "java": f"public class Solution {{\n    public Object {slug}(String input) {{\n        return null;\n    }}\n}}",
            "cpp": f'#include <string>\nusing namespace std;\nstring {slug}(string input) {{\n    return "";\n}}',
            "js": f'function {slug}(input) {{\n    return "";\n}}',
        }.get(language, "// Language not supported.")


# ------------------------
# ✅ Utility: Extract Python Function Name
# ------------------------
def extract_python_function_name(code, fallback="function_name"):
    match = re.search(r"def\s+(\w+)\s*\(", code)
    return match.group(1) if match else fallback


# ------------------------
# ✅ Run Examples (per-case driver)
# ------------------------
def run_examples(problem, code, language):
    examples = getattr(problem, "examples_group", None)
    examples = examples.examples if examples else []

    inputs = [ex.get("input") for ex in examples if ex.get("input") is not None]
    expected_outputs = [
        ex.get("output") for ex in examples if ex.get("output") is not None
    ]

    starter_code = problem.starter_code.get_code("python", slug=problem.slug)
    func_name = extract_python_function_name(
        starter_code, fallback=problem.slug.replace("-", "_")
    )

    results = []
    for i, (input_val, expected_output) in enumerate(
        zip(inputs, expected_outputs), start=1
    ):
        try:
            input_dict = (
                json.loads(input_val) if isinstance(input_val, str) else input_val
            )
            args = [input_dict[key] for key in sorted(input_dict.keys(), key=int)]
        except Exception as e:
            print(f"[ERROR] run_examples({i}): {e}")
            args = []

        if language == "python":
            driver_code = f"""
import json
if __name__ == "__main__":
    try:
        result = {func_name}(*{json.dumps(args)})
    except Exception as e:
        result = str(e)
    print(json.dumps(result))
"""
        else:
            return []

        final_code = code.strip() + "\n\n" + textwrap.dedent(driver_code)
        result_output = execute_code(final_code, language=language, input_data="")

        try:
            output_line = result_output.strip().splitlines()[-1]
            output_val = json.loads(output_line)
        except Exception as e:
            output_val = "Error"

        results.append(
            {
                "input": input_val,
                "expected": expected_output,
                "output": output_val,
                "passed": output_val == expected_output,
                "case_number": i,
            }
        )

    return results


# ------------------------
# ✅ Submit Test Cases
# ------------------------
def submit_test_cases(problem, code, language, user_id=None):
    test_cases_group = getattr(problem, "testcase_group", None)
    test_cases = test_cases_group.test_cases if test_cases_group else []

    inputs = [tc.get("input_data") for tc in test_cases]
    expected_outputs = [tc.get("output_data") for tc in test_cases]

    starter_code = problem.starter_code.get_code("python", slug=problem.slug)
    func_name = extract_python_function_name(
        starter_code, fallback=problem.slug.replace("-", "_")
    )

    results, times, passed_cases = [], [], 0

    for i, (input_val, expected_output) in enumerate(
        zip(inputs, expected_outputs), start=1
    ):
        try:
            input_dict = (
                json.loads(input_val) if isinstance(input_val, str) else input_val
            )
            args = [input_dict[key] for key in sorted(input_dict.keys(), key=int)]
        except Exception as e:
            args = []

        driver_code = f"""
import json
if __name__ == "__main__":
    try:
        result = {func_name}(*{json.dumps(args)})
    except Exception as e:
        result = str(e)
    print(json.dumps(result))
"""

        final_code = code.strip() + "\n\n" + textwrap.dedent(driver_code)
        start_time = time.time()
        result_output = execute_code(final_code, language=language, input_data="")
        time_taken = round(time.time() - start_time, 4)
        times.append(time_taken)

        try:
            output_line = result_output.strip().splitlines()[-1]
            output_val = json.loads(output_line)
        except:
            output_val = "Error"

        output_str = output_val.strip() if isinstance(output_val, str) else output_val
        expected_str = (
            expected_output.strip()
            if isinstance(expected_output, str)
            else expected_output
        )
        passed = output_str == expected_str

        results.append(
            {
                "input": input_val,
                "expected": expected_str,
                "output": output_str,
                "passed": passed,
                "case_number": i,
            }
        )

        if passed:
            passed_cases += 1
        else:
            break

    if user_id:
        log_submission_attempt(
            user_id=user_id,
            problem_id=str(problem.id),
            language=language,
            code=code,
            status="accepted" if passed_cases == len(test_cases) else "failed",
            time_taken=max(times) if times else 0,
        )

    return results, passed_cases, len(test_cases)


@login_required
def submit_comment(request, slug):
    if request.method == "POST":
        comment = request.POST.get("comment", "").strip()
        if comment:
            problem = get_object_or_404(Problem, slug=slug)
            save_comment(
                problem=problem,
                user_id=request.user.id,
                username=request.user.username,
                comment_text=comment,
            )
    return redirect("compile_with_problem", slug=slug)


from django.http import JsonResponse
from App.mongo import get_leaderboard_for_problem  # or leaderboard.py
from django.contrib.auth import get_user_model

User = get_user_model()


@login_required
def leaderboard_data(request, slug):
    from django.http import JsonResponse
    from App.mongo import get_leaderboard_for_problem
    from django.contrib.auth import get_user_model

    User = get_user_model()
    problem = get_object_or_404(Problem, slug=slug)
    user_id = str(request.user.id)

    # Get all submissions
    records = get_leaderboard_for_problem(problem.id)

    # Filter: Only accepted submissions
    accepted = [
        r for r in records if r.get("status") == "accepted" and "time_taken" in r
    ]

    # Sort by best time
    accepted.sort(key=lambda x: x["time_taken"])

    leaderboard = []
    total = len(accepted)

    for index, record in enumerate(accepted):
        uid = record.get("user_id")
        time = record.get("time_taken")
        user_obj = User.objects.filter(id=uid).first()
        username = user_obj.username if user_obj else "Anonymous"

        percentile = round((index / total) * 100, 2)

        leaderboard.append(
            {
                "username": username,
                "user_id": str(uid),
                "time_taken": time,
                "percentile": percentile,
                "is_current_user": user_id == str(uid),
            }
        )

    return JsonResponse({"data": leaderboard})
