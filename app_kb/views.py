from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from .models import Article, Category
from .forms import ArticleForm, CategoryForm

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

class ArticleListView(LoginRequiredMixin, ListView):
    model = Article
    template_name = 'app_kb/article_list.html'
    context_object_name = 'articles'
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_public=True)
        return queryset

class ArticleDetailView(LoginRequiredMixin, DetailView):
    model = Article
    template_name = 'app_kb/article_detail.html'
    context_object_name = 'article'

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_public=True)
        return queryset

class ArticleCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'app_kb/article_create.html'
    success_url = reverse_lazy('app_kb:article_list')

    def form_valid(self, form):
        messages.success(self.request, "Article created successfully!")
        return super().form_valid(form)

class ArticleUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'app_kb/article_create.html'
    context_object_name = 'article'

    def get_success_url(self):
        messages.success(self.request, "Article updated.")
        return reverse('app_kb:article_detail', kwargs={'pk': self.object.pk})

class ArticleDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Article
    template_name = 'app_kb/article_confirm_delete.html'
    success_url = reverse_lazy('app_kb:article_list')

class CategoryListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Category
    template_name = 'app_kb/category_list.html'
    context_object_name = 'categories'

class CategoryCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'app_kb/category_form.html'
    success_url = reverse_lazy('app_kb:category_list')

    def form_valid(self, form):
        messages.success(self.request, "Category created.")
        return super().form_valid(form)
