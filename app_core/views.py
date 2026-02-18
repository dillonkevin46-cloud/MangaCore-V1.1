from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    """
    Main dashboard view.
    """
    return render(request, 'app_core/dashboard.html')

def index(request):
    """
    Landing page or redirect to dashboard.
    """
    if request.user.is_authenticated:
        return dashboard(request)
    return render(request, 'app_core/index.html')
