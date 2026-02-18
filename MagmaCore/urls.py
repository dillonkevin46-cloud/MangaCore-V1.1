"""
URL configuration for MagmaCore project.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("app_core.urls")),
    path("tickets/", include("app_tickets.urls")),
    path("assets/", include("app_assets.urls")),
    path("kb/", include("app_kb.urls")),
    path("accounts/", include("django.contrib.auth.urls")), # Include auth urls for logout
]
