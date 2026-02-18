from django.urls import path
from . import views

app_name = 'app_kb'

urlpatterns = [
    path('', views.ArticleListView.as_view(), name='article_list'),
    path('create/', views.ArticleCreateView.as_view(), name='article_create'),
    path('<int:pk>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('<int:pk>/update/', views.ArticleUpdateView.as_view(), name='article_update'),
    path('<int:pk>/delete/', views.ArticleDeleteView.as_view(), name='article_delete'),

    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
]
