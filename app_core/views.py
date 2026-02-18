from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from .forms import UserCreateForm

User = get_user_model()

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

class SuperuserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

class UserListView(LoginRequiredMixin, SuperuserRequiredMixin, ListView):
    model = User
    template_name = 'app_core/user_list.html'
    context_object_name = 'users'

    def get_queryset(self):
        return User.objects.all().order_by('username')

class UserCreateView(LoginRequiredMixin, SuperuserRequiredMixin, CreateView):
    model = User
    form_class = UserCreateForm
    template_name = 'app_core/user_form.html'
    success_url = reverse_lazy('app_core:user_list')

class SettingsView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
    template_name = 'app_core/settings.html'
