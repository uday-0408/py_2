from django.shortcuts import render
from App.code_runner import execute_code
# Create your views here.
def home(request):
    """
    Render the home page.
    """
    return render(request, 'base.html')

def submit_code(request):
    """
    Handle code submission.
    """
    if request.method == 'POST':
        code = request.POST.get('codeInput')  # <-- fixed here
        if not code:
            print("No code submitted.")
            return render(request, 'submit_code.html', {'code':code,'error': 'Please enter some code.'})
        else:
            output = execute_code(code)
            if output:
                return render(request, 'submit_code.html', {'code':code,'output': output})
            else:
                return render(request, 'submit_code.html', {'code':code,'error': 'Error executing code.'})
    return render(request, 'submit_code.html')
