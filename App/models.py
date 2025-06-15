from django.db import models

# Create your models here.


class Problem(models.Model):
    DIFFICULTY_CHOICES = (
        ("Easy", "Easy"),
        ("Medium", "Medium"),
        ("Hard", "Hard"),
    )

    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)
    statement = models.TextField()
    constraints = models.TextField()
    input_format = models.TextField()
    output_format = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    tags = models.CharField(max_length=255, blank=True)  # Comma-separated tags

    def __str__(self):
        return self.title


class Example(models.Model):
    problem = models.ForeignKey(
        Problem, related_name="examples", on_delete=models.CASCADE
    )
    input_example = models.TextField()
    output_example = models.TextField()
    explanation = models.TextField(blank=True)

    def __str__(self):
        return f"Example for {self.problem.title}"


class TestCase(models.Model):
    problem = models.ForeignKey(
        Problem, related_name="testcases", on_delete=models.CASCADE
    )
    input_data = models.TextField()
    output_data = models.TextField()
    is_sample = models.BooleanField(default=False)

    def __str__(self):
        return f"TestCase for {self.problem.title}"
