from django.db import models
from django.contrib.auth.models import AbstractUser


class AppUser(AbstractUser):
    phone = models.CharField(max_length=15, unique=True)
    gender = models.CharField(max_length=20, blank=True)
    dob = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Problem(models.Model):
    DIFFICULTY_CHOICES = (
        ("Easy", "Easy"),
        ("Medium", "Medium"),
        ("Hard", "Hard"),
    )
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)
    statement = models.TextField()
    constraints = models.TextField()
    input_format = models.TextField()
    output_format = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    tags = models.CharField(max_length=255, blank=True)
    categories = models.ManyToManyField(Category, blank=True)
    function_signature = models.JSONField(
        default=dict
    )  # e.g. {"python": "def solve(a, b):", "java": "public int solve(int a, int b)"}

    def __str__(self):
        return self.title


class Example(models.Model):
    problem = models.OneToOneField(
        Problem, related_name="examples_group", on_delete=models.CASCADE
    )
    examples = (
        models.JSONField()
    )  # List of dicts like {"input": "[1,2], 3", "output": "4", "explanation": "..."}

    def __str__(self):
        return f"Examples for {self.problem.title}"


class TestCase(models.Model):
    problem = models.OneToOneField(
        Problem, on_delete=models.CASCADE, related_name="testcase_group"
    )
    test_cases = (
        models.JSONField()
    )  # List of dicts like {"input_data": "[1,2]", "output_data": "3", "hidden": true}

    def __str__(self):
        return f"Test Cases for {self.problem.title}"


class StarterCode(models.Model):
    problem = models.OneToOneField(
        Problem, on_delete=models.CASCADE, related_name="starter_code"
    )
    base_code_python = models.TextField(blank=True, null=True)
    base_code_cpp = models.TextField(blank=True, null=True)
    base_code_java = models.TextField(blank=True, null=True)
    base_code_js = models.TextField(blank=True, null=True)

    def get_code(self, lang, slug="function_name"):
        fallback_function_name = slug.replace("-", "_")
        return {
            "python": self.base_code_python,
            "cpp": self.base_code_cpp,
            "java": self.base_code_java,
            "js": self.base_code_js,
        }.get(lang, "")


class UserSubmission(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Accepted", "Accepted"),
        ("Wrong Answer", "Wrong Answer"),
        ("Error", "Error"),
        ("Time Limit Exceeded", "Time Limit Exceeded"),
    ]

    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    language = models.CharField(max_length=20)
    code = models.TextField()
    result_data = models.JSONField(default=dict)  # {"outputs": [...], "error": ""}
    status = models.CharField(max_length=30, choices=STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.problem.title} - {self.status}"


class SubmissionHistory(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    language = models.CharField(max_length=20)
    code = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"History: {self.user.username} on {self.problem.title}"


class Leaderboard(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    problems_solved = models.ManyToManyField(Problem, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.score} pts"
