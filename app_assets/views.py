import json
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Asset, Category, Location, PingRecord
from .forms import AssetForm, CategoryForm, LocationForm

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

class AssetListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Asset
    template_name = 'app_assets/asset_list.html'
    context_object_name = 'assets'
    ordering = ['name']

class AssetDetailView(LoginRequiredMixin, DetailView):
    model = Asset
    template_name = 'app_assets/asset_detail.html'
    context_object_name = 'asset'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        range_param = self.request.GET.get('range', '1h')
        now = timezone.now()

        if range_param == '1m':
            start_time = now - timedelta(minutes=1)
        elif range_param == '5m':
            start_time = now - timedelta(minutes=5)
        elif range_param == '30m':
            start_time = now - timedelta(minutes=30)
        elif range_param == '1h':
            start_time = now - timedelta(hours=1)
        elif range_param == '1d':
            start_time = now - timedelta(days=1)
        elif range_param == '1w':
            start_time = now - timedelta(weeks=1)
        elif range_param == '1mo':
            start_time = now - timedelta(days=30)
        else:
            start_time = now - timedelta(hours=1)

        records = self.object.ping_records.filter(timestamp__gte=start_time).order_by('timestamp')

        timestamps = [record.timestamp.strftime('%H:%M:%S' if range_param in ['1m', '5m', '30m', '1h'] else '%Y-%m-%d %H:%M') for record in records]
        latencies = [record.latency_ms if record.latency_ms is not None else 0 for record in records]
        packet_losses = [record.packet_loss for record in records]

        context['timestamps_json'] = json.dumps(timestamps)
        context['latencies_json'] = json.dumps(latencies)
        context['packet_losses_json'] = json.dumps(packet_losses)
        context['selected_range'] = range_param

        return context

class AssetCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Asset
    form_class = AssetForm
    template_name = 'app_assets/asset_create.html'
    success_url = reverse_lazy('app_assets:asset_list')

    def form_valid(self, form):
        messages.success(self.request, "Asset created successfully!")
        return super().form_valid(form)

class AssetUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Asset
    form_class = AssetForm
    template_name = 'app_assets/asset_create.html'
    context_object_name = 'asset'

    def get_success_url(self):
        messages.success(self.request, "Asset updated.")
        return reverse('app_assets:asset_detail', kwargs={'pk': self.object.pk})

class AssetDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Asset
    template_name = 'app_assets/asset_confirm_delete.html'
    success_url = reverse_lazy('app_assets:asset_list')

class CategoryListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Category
    template_name = 'app_assets/category_list.html'
    context_object_name = 'categories'

class CategoryCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'app_assets/category_form.html'
    success_url = reverse_lazy('app_assets:category_list')

    def form_valid(self, form):
        messages.success(self.request, "Category created.")
        return super().form_valid(form)

class LocationListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Location
    template_name = 'app_assets/location_list.html'
    context_object_name = 'locations'

class LocationCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Location
    form_class = LocationForm
    template_name = 'app_assets/location_form.html'
    success_url = reverse_lazy('app_assets:location_list')

    def form_valid(self, form):
        messages.success(self.request, "Location created.")
        return super().form_valid(form)

class MonitoringDashboardView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Asset
    template_name = 'app_assets/monitoring_dashboard.html'
    context_object_name = 'monitored_assets'

    def get_queryset(self):
        return Asset.objects.filter(is_monitored=True)
