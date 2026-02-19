from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from .models import Asset, Category, Location
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
