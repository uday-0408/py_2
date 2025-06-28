from App.models import Problem, Example, TestCase

Problem.objects.all().delete()

problems_data = [
    {
        "title": "Missing Number",
        "slug": "missing-number",
        "statement": "Given an array containing n distinct numbers taken from 0 to n, find the missing number.",
        "constraints": "The array length is between 1 and 10^4.",
        "input_format": "An array of distinct integers.",
        "output_format": "An integer representing the missing number.",
        "difficulty": "Easy",
        "tags": "array, math",
        "examples": [
            {
                "input_example": "[3, 0, 1]",
                "output_example": "2",
                "explanation": "The missing number is 2.",
            },
            {
                "input_example": "[9, 6, 4, 2, 3, 5, 7, 0, 1]",
                "output_example": "8",
                "explanation": "The missing number is 8.",
            },
        ],
        "test_cases": [
            {"input_data": "[3, 0, 1]", "output_data": "2", "is_sample": True},
            {"input_data": "[0, 1]", "output_data": "2", "is_sample": True},
            {
                "input_data": "[9, 6, 4, 2, 3, 5, 7, 0, 1]",
                "output_data": "8",
                "is_sample": False,
            },
            {"input_data": "[0]", "output_data": "1", "is_sample": False},
            {"input_data": "[1, 2, 3, 4, 5]", "output_data": "0", "is_sample": False},
        ],
    },
    {
        "title": "Two Sum II - Sorted Input",
        "slug": "two-sum-ii",
        "statement": "Given an array of integers sorted in ascending order, find two that add up to a target.",
        "constraints": "Array length between 2 and 3*10^4.",
        "input_format": "An array of integers and a target integer.",
        "output_format": "An array of two indices.",
        "difficulty": "Easy",
        "tags": "array, two-pointers",
        "examples": [
            {
                "input_example": "[2, 7, 11, 15], target = 9",
                "output_example": "[1, 2]",
                "explanation": "2 + 7 = 9",
            },
            {
                "input_example": "[2, 3, 4], target = 6",
                "output_example": "[1, 3]",
                "explanation": "2 + 4 = 6",
            },
        ],
        "test_cases": [
            {
                "input_data": "[2, 7, 11, 15], target = 9",
                "output_data": "[1, 2]",
                "is_sample": True,
            },
            {
                "input_data": "[2, 3, 4], target = 6",
                "output_data": "[1, 3]",
                "is_sample": True,
            },
            {
                "input_data": "[-1, 0], target = -1",
                "output_data": "[1, 2]",
                "is_sample": False,
            },
            {
                "input_data": "[5, 25, 75], target = 100",
                "output_data": "[2, 3]",
                "is_sample": False,
            },
            {
                "input_data": "[1, 2, 3, 4, 4, 9, 56, 90], target = 8",
                "output_data": "[4, 5]",
                "is_sample": False,
            },
        ],
    },
]

for pdata in problems_data:
    problem = Problem.objects.create(
        title=pdata["title"],
        slug=pdata["slug"],
        statement=pdata["statement"],
        constraints=pdata["constraints"],
        input_format=pdata["input_format"],
        output_format=pdata["output_format"],
        difficulty=pdata["difficulty"],
        tags=pdata["tags"],
    )

    for ex in pdata["examples"]:
        Example.objects.create(
            problem=problem,
            input_example=ex["input_example"],
            output_example=ex["output_example"],
            explanation=ex["explanation"],
        )

    for tc in pdata["test_cases"]:
        TestCase.objects.create(
            problem=problem,
            input_data=tc["input_data"],
            output_data=tc["output_data"],
            is_sample=tc["is_sample"],
        )

print("✅ Database seeded successfully.")
