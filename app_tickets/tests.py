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

    def test_my_tickets_filter(self):
        other_user = User.objects.create_user(username='other', password='password')
        t1 = Ticket.objects.create(title='My Ticket', description='Desc', creator=self.user)
        t2 = Ticket.objects.create(title='Other Ticket', description='Desc', creator=other_user)

        response = self.client.get(reverse('app_tickets:ticket_list'), {'filter': 'my_tickets'})
        self.assertContains(response, 'My Ticket')
        self.assertNotContains(response, 'Other Ticket')

    def test_staff_fields_in_form(self):
        # Staff should see assigned_agent
        self.client.logout()
        staff_user = User.objects.create_user(username='staff', password='password', is_staff=True)
        self.client.login(username='staff', password='password')
        response = self.client.get(reverse('app_tickets:ticket_create'))
        self.assertContains(response, 'assigned_agent')

    def test_regular_user_fields_in_form(self):
        # Regular user should NOT see assigned_agent
        response = self.client.get(reverse('app_tickets:ticket_create'))
        self.assertNotContains(response, 'assigned_agent')
