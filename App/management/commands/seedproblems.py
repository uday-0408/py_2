from django.utils.text import slugify
from App.models import Problem, Category, Example, TestCase, StarterCode


def seed_problems():
    problems_data = [
        {
            "id": 1,
            "title": "Find Missing Number",
            "statement": "Given an array containing n distinct numbers taken from 0 to n, find the one number that is missing from the array.",
            "constraints": "1 <= n <= 10^4\nEach element is unique and between 0 and n inclusive.",
            "input_format": "A list of integers representing the array.",
            "output_format": "An integer representing the missing number.",
            "difficulty": "Easy",
            "tags": "array,math",
            "function_signature": {
                "python": "def find_missing_number(nums):",
                "java": "public int findMissingNumber(int[] nums)",
                "cpp": "int findMissingNumber(vector<int>& nums)",
                "js": "function findMissingNumber(nums)",
            },
            "examples": [
                {
                    "input": {"1": [3, 0, 1]},
                    "output": 2,
                    "explanation": "0,1,3 => 2 missing",
                },
                {"input": {"1": [0, 1]}, "output": 2, "explanation": "Missing 2"},
            ],
            "test_cases": [
                {"input_data": {"1": [3, 0, 1]}, "output_data": 2, "hidden": False},
                {"input_data": {"1": [0, 1]}, "output_data": 2, "hidden": False},
                {
                    "input_data": {"1": [9, 6, 4, 2, 3, 5, 7, 0, 1]},
                    "output_data": 8,
                    "hidden": True,
                },
                {"input_data": {"1": [0]}, "output_data": 1, "hidden": True},
                {"input_data": {"1": [1]}, "output_data": 0, "hidden": True},
            ],
            "starter_code": {
                "python": "def find_missing_number(nums):\n    # Write your code here\n    pass",
                "cpp": "#include <vector>\nusing namespace std;\nint findMissingNumber(vector<int>& nums) {\n    // Write your code here\n    return -1;\n}",
                "java": "public class Solution {\n    public int findMissingNumber(int[] nums) {\n        // Write your code here\n        return -1;\n    }\n}",
                "js": "function findMissingNumber(nums) {\n    // Write your code here\n    return -1;\n}",
            },
            "category": {
                "name": "Math",
                "description": "Problems based on mathematical logic and operations.",
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
