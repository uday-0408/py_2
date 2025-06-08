from django.shortcuts import render
from App.code_runner import execute_code
# super use :uday ,password:uday@0408
def home_page(request):
    return render(request, 'home.html')

def compile_code(request):
    """
    Handle code compilation and return the output.
    """
    if request.method == 'POST':
        code = request.POST.get('code')
        input_data = request.POST.get('input_data', '')
        language = request.POST.get('language')

        if not code:
            return render(request, 'compile.html', {
                'error': 'Please enter some code.',
                'code': code,
                'input_data': input_data,
                'language': language
            })

        output = execute_code(code, language_id=language_id_map.get(language, 71), input_data=input_data)
        return render(request, 'output.html', {
            'code': code,
            'input_data': input_data,
            'output': output,
            'language': language
        })

    return render(request, 'compile.html')

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


# Map language names to Judge0 IDs
language_id_map = {
    'python': 71,
    'cpp': 54,
    'java': 62,
    'javascript': 63,
    # Add more mappings as needed
}
