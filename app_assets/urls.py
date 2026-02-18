from django.urls import path
from . import views

app_name = 'app_assets'

urlpatterns = [
    path('', views.AssetListView.as_view(), name='asset_list'),
    path('create/', views.AssetCreateView.as_view(), name='asset_create'),
    path('<int:pk>/update/', views.AssetUpdateView.as_view(), name='asset_update'),
    path('<int:pk>/delete/', views.AssetDeleteView.as_view(), name='asset_delete'),

    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/update/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),

    path('locations/', views.LocationListView.as_view(), name='location_list'),
    path('locations/create/', views.LocationCreateView.as_view(), name='location_create'),
    path('locations/<int:pk>/update/', views.LocationUpdateView.as_view(), name='location_update'),
    path('locations/<int:pk>/delete/', views.LocationDeleteView.as_view(), name='location_delete'),
]
