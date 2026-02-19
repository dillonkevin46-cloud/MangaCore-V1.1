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
    is_monitored = models.BooleanField(default=False)
    alert_email = models.EmailField(blank=True, null=True, help_text="Email to notify if device goes offline")
    serial_number = models.CharField(max_length=100, blank=True)
    model_no = models.CharField(max_length=100, blank=True)
    make = models.CharField(max_length=100, blank=True)
    specifications = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.category})"

class PingRecord(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='ping_records')
    timestamp = models.DateTimeField(auto_now_add=True)
    latency_ms = models.FloatField(null=True, blank=True)
    packet_loss = models.FloatField(default=0.0)
    is_online = models.BooleanField(default=False)

    def __str__(self):
        return f"Ping for {self.asset.name} at {self.timestamp}"
