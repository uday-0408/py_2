import os
import sys
import django
import json
from django.utils.text import slugify

# Add project root to sys.path so App can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "compiler.settings")
django.setup()

# Now import models after setup
from App.models import Problem, Category, Example, TestCase, StarterCode


def seed_problems():
    problems_data = [
        {
            "title": "Reverse Integer",
            "statement": "Given a signed 32-bit integer x, return x with its digits reversed. If reversing x causes the value to go outside the signed 32-bit integer range, return 0.",
            "constraints": "-2^31 <= x <= 2^31 - 1",
            "input_format": "An integer x.",
            "output_format": "An integer, the reversed value or 0 if overflow.",
            "difficulty": "Medium",
            "tags": "math",
            "function_signature": {
                "python": "def reverse(x):",
                "java": "public int reverse(int x)",
                "cpp": "int reverse(int x)",
                "js": "function reverse(x)",
            },
            "examples": [
                {"input": {"1": 123}, "output": 321, "explanation": "Simple reverse."},
                {
                    "input": {"1": -123},
                    "output": -321,
                    "explanation": "Negative reversed.",
                },
            ],
            "test_cases": [
                {"input_data": {"1": 123}, "output_data": 321, "hidden": False},
                {"input_data": {"1": -123}, "output_data": -321, "hidden": False},
                {"input_data": {"1": 120}, "output_data": 21, "hidden": True},
                {"input_data": {"1": 0}, "output_data": 0, "hidden": True},
                {"input_data": {"1": 1534236469}, "output_data": 0, "hidden": True},
            ],
            "starter_code": {
                "python": "def reverse(x):\n    # Write your code here\n    pass",
                "cpp": "int reverse(int x) {\n    // Write your code here\n    return 0;\n}",
                "java": "public class Solution {\n    public int reverse(int x) {\n        // Write your code here\n        return 0;\n    }\n}",
                "js": "function reverse(x) {\n    // Write your code here\n    return 0;\n}",
            },
            "category": {
                "name": "Math",
                "description": "Problems based on mathematical operations and edge cases.",
            },
        }
    ]

    for pdata in problems_data:
        category_obj, _ = Category.objects.get_or_create(
            name=pdata["category"]["name"],
            defaults={"description": pdata["category"]["description"]},
        )

        slug = slugify(pdata["title"])
        problem, _ = Problem.objects.get_or_create(
            title=pdata["title"],
            slug=slug,
            defaults={
                "statement": pdata["statement"],
                "constraints": pdata["constraints"],
                "input_format": pdata["input_format"],
                "output_format": pdata["output_format"],
                "difficulty": pdata["difficulty"],
                "tags": pdata["tags"],
                "function_signature": pdata["function_signature"],
            },
        )
        problem.categories.add(category_obj)

        Example.objects.update_or_create(
            problem=problem, defaults={"examples": pdata["examples"]}
        )

        TestCase.objects.update_or_create(
            problem=problem, defaults={"test_cases": pdata["test_cases"]}
        )

        StarterCode.objects.update_or_create(
            problem=problem,
            defaults={
                "base_code_python": pdata["starter_code"]["python"],
                "base_code_cpp": pdata["starter_code"]["cpp"],
                "base_code_java": pdata["starter_code"]["java"],
                "base_code_js": pdata["starter_code"]["js"],
            },
        )

    print("✅ Problems seeded successfully.")


if __name__ == "__main__":
    seed_problems()
