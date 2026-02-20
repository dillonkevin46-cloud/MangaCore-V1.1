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

class IndexView(TemplateView):
    template_name = 'app_core/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            # 1. Total Users
            total_users = User.objects.count()

            # 2. Total Tickets
            total_tickets = Ticket.objects.count()

            # 3. Open Tickets (OPEN or IN_PROGRESS)
            open_tickets = Ticket.objects.filter(
                status__in=[Ticket.Status.OPEN, Ticket.Status.IN_PROGRESS]
            ).count()

            # 4. Total Assets
            total_assets = Asset.objects.count()

            # 5. Online Assets (Pure Python logic as requested)
            monitored_assets = Asset.objects.filter(is_monitored=True)
            online_assets = sum(1 for a in monitored_assets if a.current_status)

            context.update({
                'total_users': total_users,
                'total_tickets': total_tickets,
                'open_tickets': open_tickets,
                'total_assets': total_assets,
                'online_assets': online_assets,
            })

            # Chart Data
            ticket_stats = {
                'OPEN': Ticket.objects.filter(status=Ticket.Status.OPEN).count(),
                'IN_PROGRESS': Ticket.objects.filter(status=Ticket.Status.IN_PROGRESS).count(),
                'RESOLVED': Ticket.objects.filter(status=Ticket.Status.RESOLVED).count(),
                'CLOSED': Ticket.objects.filter(status=Ticket.Status.CLOSED).count(),
            }

            asset_stats = {
                'online': online_assets,
                'offline': monitored_assets.count() - online_assets
            }

            context['ticket_stats_json'] = json.dumps(ticket_stats)
            context['asset_stats_json'] = json.dumps(asset_stats)

        return context

# Use as_view() directly for the URLs to pick up
index = IndexView.as_view()
dashboard = login_required(IndexView.as_view())

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
