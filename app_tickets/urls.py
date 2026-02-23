from django.urls import path
from . import views

app_name = 'app_tickets'

urlpatterns = [
    path('', views.TicketListView.as_view(), name='ticket_list'),
    path('create/', views.TicketCreateView.as_view(), name='ticket_create'),
    path('<int:pk>/', views.TicketDetailView.as_view(), name='ticket_detail'),
    path('<int:pk>/update/', views.TicketUpdateView.as_view(), name='ticket_update'),
    path('<int:pk>/delete/', views.TicketDeleteView.as_view(), name='ticket_delete'),
    path('<int:pk>/comment/', views.TicketAddCommentView.as_view(), name='ticket_add_comment'),

    path('categories/', views.TicketCategoryListView.as_view(), name='category_list'),
    path('categories/add/', views.TicketCategoryCreateView.as_view(), name='category_add'),
    path('categories/<int:pk>/edit/', views.TicketCategoryUpdateView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', views.TicketCategoryDeleteView.as_view(), name='category_delete'),
]
