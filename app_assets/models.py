from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Asset(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='assets')
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='assets')
    assigned_to = models.CharField(max_length=200, blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    model_no = models.CharField(max_length=100, blank=True)
    make = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.category})"
