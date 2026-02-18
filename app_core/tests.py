from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class UserManagementTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(username='admin', password='password', email='admin@example.com')
        self.staff_user = User.objects.create_user(username='staff', password='password', is_staff=True)
        self.regular_user = User.objects.create_user(username='user', password='password')

    def test_user_list_access_superuser(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('app_core:user_list'))
        self.assertEqual(response.status_code, 200)

    def test_user_list_access_denied_staff(self):
        self.client.login(username='staff', password='password')
        response = self.client.get(reverse('app_core:user_list'))
        self.assertEqual(response.status_code, 403)

    def test_user_list_access_denied_regular(self):
        self.client.login(username='user', password='password')
        response = self.client.get(reverse('app_core:user_list'))
        self.assertEqual(response.status_code, 403)

    def test_user_create_access_superuser(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('app_core:user_create'))
        self.assertEqual(response.status_code, 200)

    def test_user_create_access_denied_staff(self):
        self.client.login(username='staff', password='password')
        response = self.client.get(reverse('app_core:user_create'))
        self.assertEqual(response.status_code, 403)
