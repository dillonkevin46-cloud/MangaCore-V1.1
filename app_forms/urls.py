
from django.urls import path
from . import views

app_name = 'app_forms'

urlpatterns = [
    path('', views.FormListView.as_view(), name='form_list'),
    path('create/', views.FormCreateView.as_view(), name='form_create'),
    path('<int:pk>/builder/', views.FormBuilderView.as_view(), name='form_builder'),
    path('<int:pk>/responses/', views.FormResponsesView.as_view(), name='form_responses'),
    path('<int:pk>/share/', views.FormShareEmailView.as_view(), name='form_share_email'),
    path('<int:pk>/serve/', views.FormServeView.as_view(), name='form_serve'), # Public link
]
