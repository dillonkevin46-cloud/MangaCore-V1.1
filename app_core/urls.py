from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'app_core'

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/create/', views.UserCreateView.as_view(), name='user_create'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),

    path('checklist/', views.ChecklistView.as_view(), name='checklist'),
    path('checklist/add/', views.AddChecklistTaskView.as_view(), name='checklist_add'),
    path('checklist/toggle/<int:pk>/', views.ToggleChecklistTaskView.as_view(), name='checklist_toggle'),

    path('contacts/', views.ContactListView.as_view(), name='contact_list'),
    path('contacts/add/', views.ContactCreateView.as_view(), name='contact_add'),
]
