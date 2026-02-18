from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Ticket

User = get_user_model()

class TicketTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

    def test_ticket_list_view(self):
        response = self.client.get(reverse('app_tickets:ticket_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_tickets/ticket_list.html')

    def test_ticket_create_view(self):
        response = self.client.get(reverse('app_tickets:ticket_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_tickets/ticket_create.html')
