"""
URL configuration for MagmaCore project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("app_core.urls")),
    path("tickets/", include("app_tickets.urls")),
    path("assets/", include("app_assets.urls")),
    path("kb/", include("app_kb.urls")),
    path("forms/", include("app_forms.urls")),
    path("accounts/", include("django.contrib.auth.urls")), # Include auth urls for logout
    path('ckeditor/', include('ckeditor_uploader.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
