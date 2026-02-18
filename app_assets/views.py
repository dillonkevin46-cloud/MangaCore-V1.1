from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Asset, Category
from .forms import AssetForm, CategoryForm

class AssetListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Asset
    template_name = 'app_assets/asset_list.html'
    context_object_name = 'assets'
    paginate_by = 10

    def get_queryset(self):
        return super().get_queryset().order_by('-created_at')

    def test_func(self):
        return self.request.user.is_staff

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
