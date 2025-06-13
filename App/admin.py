from django.contrib import admin

# Register your models here.

from .models import Problem, Example, TestCase

admin.site.register(Problem)
admin.site.register(Example)
admin.site.register(TestCase)