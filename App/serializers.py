from rest_framework import serializers
from .models import Problem, Example

class ExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Example
        fields = ['input_example', 'output_example', 'explanation']

class ProblemSerializer(serializers.ModelSerializer):
    examples = ExampleSerializer(many=True, read_only=True)  # related_name='examples' in model

    class Meta:
        model = Problem
        fields = ['id', 'title', 'slug', 'statement', 'constraints', 'input_format', 'output_format', 'difficulty', 'tags', 'examples']
