from django.urls import path
from . import views

app_name = 'app_tickets'

urlpatterns = [
    path('', views.TicketListView.as_view(), name='ticket_list'),
    path('archive/', views.TicketArchiveListView.as_view(), name='ticket_archive'),
    path('create/', views.TicketCreateView.as_view(), name='ticket_create'),
    path('export-csv/', views.TicketExportCSVView.as_view(), name='ticket_export_csv'),
    path('<int:pk>/', views.TicketDetailView.as_view(), name='ticket_detail'),
    path('<int:pk>/update/', views.TicketUpdateView.as_view(), name='ticket_update'),
    path('<int:pk>/delete/', views.TicketDeleteView.as_view(), name='ticket_delete'),

    path('categories/', views.TicketCategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.TicketCategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/update/', views.TicketCategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', views.TicketCategoryDeleteView.as_view(), name='category_delete'),
]
