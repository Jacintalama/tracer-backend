# tracer_backend/urls.py

"""
URL configuration for tracer_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from .views import home

urlpatterns = [
    # Your existing home view
    path('', home, name='home'),

    # Admin site
    path('admin/', admin.site.urls),

    # Include all OCR-related URLs under /api/ocr/
    path('api/ocr/', include('ocr.urls')),
]
