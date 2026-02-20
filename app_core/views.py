import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import UserCreateForm
from .models import UserChecklistTask, AppNotification, AddressBookContact
from app_tickets.models import Ticket
from app_assets.models import Asset, Category

User = get_user_model()

@login_required
def dashboard(request):
    """
    Main dashboard view.
    """
    # Ticket Stats
    ticket_stats = {
        'OPEN': Ticket.objects.filter(status=Ticket.Status.OPEN).count(),
        'IN_PROGRESS': Ticket.objects.filter(status=Ticket.Status.IN_PROGRESS).count(),
        'RESOLVED': Ticket.objects.filter(status=Ticket.Status.RESOLVED).count(),
        'CLOSED': Ticket.objects.filter(status=Ticket.Status.CLOSED).count(),
    }

    # Asset Stats
    monitored_assets_count = Asset.objects.filter(is_monitored=True).count()
    # Simple logic: assume assets with IP and monitored=True are "Online" if we had a field,
    # but for now we might count based on latest PingRecord.
    # To simplify for the dashboard pie chart:
    # Online = Monitored assets where last PingRecord.is_online = True
    # Offline = Monitored assets where last PingRecord.is_online = False
    # Unknown = Monitored assets with no records

    online_count = 0
    offline_count = 0
    unknown_count = 0

    monitored_assets = Asset.objects.filter(is_monitored=True)
    for asset in monitored_assets:
        last_record = asset.ping_records.order_by('-timestamp').first()
        if last_record:
            if last_record.is_online:
                online_count += 1
            else:
                offline_count += 1
        else:
            unknown_count += 1

    asset_stats = {
        'monitored': monitored_assets_count,
        'online': online_count,
        'offline': offline_count,
        'unknown': unknown_count
    }

    # Category Based Stats for Stacked Bar Chart
    categories = Category.objects.all()
    category_names = []
    cat_online_counts = []
    cat_offline_counts = []

    for cat in categories:
        # Get monitored assets in this category
        cat_assets = Asset.objects.filter(category=cat, is_monitored=True)
        c_online = 0
        c_offline = 0

        for asset in cat_assets:
            if asset.current_status:
                c_online += 1
            else:
                c_offline += 1

        if c_online > 0 or c_offline > 0:
            category_names.append(cat.name)
            cat_online_counts.append(c_online)
            cat_offline_counts.append(c_offline)

    context = {
        'ticket_stats_json': json.dumps(ticket_stats),
        'asset_stats_json': json.dumps(asset_stats),
        'category_names_json': json.dumps(category_names),
        'cat_online_json': json.dumps(cat_online_counts),
        'cat_offline_json': json.dumps(cat_offline_counts),
    }
    return render(request, 'app_core/index.html', context)

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

class ChecklistView(LoginRequiredMixin, ListView):
    model = UserChecklistTask
    template_name = 'app_core/checklist.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        return UserChecklistTask.objects.filter(user=self.request.user).order_by('is_completed', '-created_at')

class AddChecklistTaskView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        task_text = request.POST.get('task')
        if task_text:
            UserChecklistTask.objects.create(user=request.user, task=task_text)
        return redirect('app_core:checklist')

class ToggleChecklistTaskView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        task = get_object_or_404(UserChecklistTask, pk=pk, user=request.user)
        task.is_completed = not task.is_completed
        task.save()
        return redirect('app_core:checklist')

class ContactListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = AddressBookContact
    template_name = 'app_core/contact_list.html'
    context_object_name = 'contacts'
    ordering = ['name']

class ContactCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = AddressBookContact
    fields = ['name', 'email', 'department']
    template_name = 'app_core/contact_form.html'
    success_url = reverse_lazy('app_core:contact_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field in form.fields.values():
            field.widget.attrs.update({'class': 'form-control bg-transparent text-white'})
        return form
