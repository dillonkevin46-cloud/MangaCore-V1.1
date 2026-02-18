from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Article, Category
from .forms import ArticleForm, CategoryForm

class ArticleListView(LoginRequiredMixin, ListView):
    model = Article
    template_name = 'app_kb/article_list.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_public=True)

        search = self.request.GET.get('q')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search)
            )
        return queryset.order_by('-created_at')

class ArticleDetailView(LoginRequiredMixin, DetailView):
    model = Article
    template_name = 'app_kb/article_detail.html'
    context_object_name = 'article'

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_public=True)
        return queryset

class ArticleCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'app_kb/article_create.html'
    success_url = reverse_lazy('app_kb:article_list')

    def test_func(self):
        return self.request.user.is_staff

class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'app_kb/article_create.html'
    success_url = reverse_lazy('app_kb:article_list')

    def test_func(self):
        return self.request.user.is_staff

class ArticleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Article
    template_name = 'app_kb/article_confirm_delete.html'
    success_url = reverse_lazy('app_kb:article_list')

    def test_func(self):
        return self.request.user.is_staff

class CategoryListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Category
    template_name = 'app_kb/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return super().get_queryset().order_by('name')

    def test_func(self):
        return self.request.user.is_staff

class CategoryCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'app_kb/category_form.html'
    success_url = reverse_lazy('app_kb:category_list')

    def test_func(self):
        return self.request.user.is_staff

class CategoryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Category
    template_name = 'app_kb/category_confirm_delete.html'
    success_url = reverse_lazy('app_kb:category_list')

    def test_func(self):
        return self.request.user.is_staff
