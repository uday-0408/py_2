from django.shortcuts import get_object_or_404, render
from App.code_runner import execute_code
from rest_framework import generics
from .models import Problem
from .serializers import ProblemSerializer

class ProblemListAPIView(generics.ListAPIView):
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer

class ProblemDetailAPIView(generics.RetrieveAPIView):
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer
    lookup_field = 'slug'

def home_page(request):
    return render(request, 'home.html')

def problem_list(request):
    problems = Problem.objects.all()
    return render(request, 'problems.html', {'problems': problems})

def compile_code(request, slug=None):
    problem = None
    # print(f"Problem slug from URL: {slug}")
    if slug:
        problem = get_object_or_404(Problem, slug=slug)

    if request.method == 'POST':
        code = request.POST.get('code')
        input_data = request.POST.get('input_data', '')
        language = request.POST.get('language')

        if not code:
            return render(request, 'compile.html', {
                'error': 'Please enter some code.',
                'code': code,
                'input_data': input_data,
                'language': language,
                'problem': problem
            })

        output = execute_code(code, language_id=language_id_map.get(language, 71), input_data=input_data)
        return render(request, 'compile.html', {
            'code': code,
            'input_data': input_data,
            'output': output,
            'language': language,
            'problem': problem
        })

    return render(request, 'compile.html', {
        'problem': problem
    })

def execution_result(request):
    return render(request, 'output.html')

def languages_supported(request):
    return render(request, 'languages.html')

def about_page(request):
    return render(request, 'about.html')

def contact_page(request):
    return render(request, 'contact.html')

def user_history(request):
    return render(request, 'history.html')

# Language map
language_id_map = {
    'python': 71,
    'cpp': 54,
    'java': 62,
    'javascript': 63,
}
