import json
from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone
from datetime import timedelta
from .models import Asset, Category, Location, PingRecord
from .forms import AssetForm, CategoryForm, LocationForm

class AssetListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Asset
    template_name = 'app_assets/asset_list.html'
    context_object_name = 'assets'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all().order_by('name')
        context['selected_category'] = self.request.GET.get('category')
        return context

    def test_func(self):
        return self.request.user.is_staff

class AssetDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Asset
    template_name = 'app_assets/asset_detail.html'
    context_object_name = 'asset'

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get Ping data for the last 24 hours
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        records = PingRecord.objects.filter(asset=self.object, timestamp__gte=last_24h).order_by('timestamp')

        timestamps = [record.timestamp.strftime('%Y-%m-%d %H:%M') for record in records]
        latencies = [record.latency_ms if record.latency_ms is not None else 0 for record in records]

        context['ping_timestamps'] = json.dumps(timestamps)
        context['ping_latencies'] = json.dumps(latencies)

        return context

class AssetCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Asset
    form_class = AssetForm
    template_name = 'app_assets/asset_create.html'
    success_url = reverse_lazy('app_assets:asset_list')

    def test_func(self):
        return self.request.user.is_staff

class AssetUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Asset
    form_class = AssetForm
    template_name = 'app_assets/asset_create.html'
    success_url = reverse_lazy('app_assets:asset_list')

    def test_func(self):
        return self.request.user.is_staff

class AssetDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Asset
    template_name = 'app_assets/asset_confirm_delete.html'
    success_url = reverse_lazy('app_assets:asset_list')

    def test_func(self):
        return self.request.user.is_staff

class CategoryListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Category
    template_name = 'app_assets/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return super().get_queryset().order_by('name')

    def test_func(self):
        return self.request.user.is_staff

class CategoryCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'app_assets/category_create.html'
    success_url = reverse_lazy('app_assets:category_list')

    def test_func(self):
        return self.request.user.is_staff

class CategoryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'app_assets/category_create.html'
    success_url = reverse_lazy('app_assets:category_list')

    def test_func(self):
        return self.request.user.is_staff

class CategoryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Category
    template_name = 'app_assets/category_confirm_delete.html'
    success_url = reverse_lazy('app_assets:category_list')

    def test_func(self):
        return self.request.user.is_staff

class LocationListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Location
    template_name = 'app_assets/location_list.html'
    context_object_name = 'locations'

    def get_queryset(self):
        return super().get_queryset().order_by('name')

    def test_func(self):
        return self.request.user.is_staff

class LocationCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Location
    form_class = LocationForm
    template_name = 'app_assets/location_form.html'
    success_url = reverse_lazy('app_assets:location_list')

    def test_func(self):
        return self.request.user.is_staff

class LocationUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Location
    form_class = LocationForm
    template_name = 'app_assets/location_form.html'
    success_url = reverse_lazy('app_assets:location_list')

    def test_func(self):
        return self.request.user.is_staff

class LocationDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Location
    template_name = 'app_assets/location_confirm_delete.html'
    success_url = reverse_lazy('app_assets:location_list')

    def test_func(self):
        return self.request.user.is_staff
