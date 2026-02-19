from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Create your models here.

class AppNotification(models.Model):
    TYPE_CHOICES = [
        ('WARNING', 'Warning'),
        ('INFO', 'Info'),
    ]
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    notification_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='INFO')

    def __str__(self):
        return f"{self.notification_type}: {self.message}"

class UserChecklistTask(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='checklist_tasks')
    task = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.task}"
