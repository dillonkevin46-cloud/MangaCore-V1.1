from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Article

User = get_user_model()

class KBTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.staff_user = User.objects.create_user(username='staffuser', password='password', is_staff=True)

    def test_article_list_access_allowed_for_regular_user(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('app_kb:article_list'))
        self.assertEqual(response.status_code, 200)

    def test_article_create_access_denied_for_regular_user(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('app_kb:article_create'))
        self.assertEqual(response.status_code, 403)

    def test_article_create_access_allowed_for_staff_user(self):
        self.client.login(username='staffuser', password='password')
        response = self.client.get(reverse('app_kb:article_create'))
        self.assertEqual(response.status_code, 200)
