from django.shortcuts import get_object_or_404, render
from App.code_runner2 import execute_code
from rest_framework import generics
from .models import Problem
from .serializers import ProblemSerializer


# username:Uday password:Uday1234
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


def compile_code(request, slug=None):
    problem = None
    if slug:
        print(f"Slug provided: {slug}")
        problem = get_object_or_404(Problem, slug=slug)
        print(f"Problem fetched: {problem.title}")

    if request.method == "POST":
        print("POST request received")
        code = request.POST.get("code")
        language = request.POST.get("language")
        print(f"Language selected: {language}")
        print(f"Code length: {len(code)} characters")

        if problem:
            print("Problem exists, fetching test cases...")
            test_cases = problem.testcases.all()  # ✅ changed here
            print(f"Total test cases found: {test_cases.count()}")

            results = []
            for tc in test_cases:
                input_data = tc.input_data.strip()
                expected_output = tc.output_data.strip()

                result = execute_code(
                    code,
                    language_id=language_id_map.get(language, 71),
                    input_data=input_data,
                )

                actual_output = result.strip()
                is_correct = actual_output == expected_output

                results.append(
                    {
                        "input": input_data,
                        "expected": expected_output,
                        "actual": actual_output,
                        "correct": is_correct,
                    }
                )
            ans = {
                "code": code,
                "language": language,
                "problem": problem,
                "test_results": results,
            }
            print(ans)

            print("=== All test cases processed ===")
            return render(
                request,
                "compile.html",
                {
                    "code": code,
                    "language": language,
                    "problem": problem,
                    "test_results": results,
                },
            )

        else:
            input_data = request.POST.get("input_data", "")
            output = execute_code(
                code,
                language_id=language_id_map.get(language, 71),
                input_data=input_data,
            )
            return render(
                request,
                "compile.html",
                {
                    "code": code,
                    "input_data": input_data,
                    "output": output,
                    "language": language,
                },
            )

    return render(request, "compile.html", {"problem": problem})


def compile_code1(request, slug=None):
    problem = None
    # print(f"Problem slug from URL: {slug}")
    if slug:
        problem = get_object_or_404(Problem, slug=slug)
        test_cases = problem.testcases.filter(is_sample=False)

    if request.method == "POST":
        pre = """
            x=input()
            arr=[]
            for i in range(int(x)):
                arr.append(int(input()))
            target=int(input())
            """
        post = """
                arr=two_som(arr,target)
                for i in arr:
                    print(i,end=' ')
                """
        print(f"Problem: {problem}")
        print(f"Test cases: {test_cases}")
        if problem and not test_cases:
            code = pre + problem.code + post
        # elif problem and test_cases:

        else:
            code = request.POST.get("code", "")
        code = request.POST.get("code")
        input_data = request.POST.get("input_data", "")
        language = request.POST.get("language")

        if not code:
            return render(
                request,
                "compile.html",
                {
                    "error": "Please enter some code.",
                    "code": code,
                    "input_data": input_data,
                    "language": language,
                    "problem": problem,
                },
            )

        output = execute_code(
            code, language_id=language_id_map.get(language, 71), input_data=input_data
        )
        return render(
            request,
            "compile.html",
            {
                "code": code,
                "input_data": input_data,
                "output": output,
                "language": language,
                "problem": problem,
            },
        )

    return render(request, "compile.html", {"problem": problem})


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
