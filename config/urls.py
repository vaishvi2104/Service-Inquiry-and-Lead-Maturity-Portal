"""
Root URL Configuration for Start-Up Sahay Portal.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Built-in Django Admin (trusted administrative backend)
    path('admin/', admin.site.urls),

    # Public Customer Portal
    path('', include('inquiries.urls', namespace='public')),

    # Restricted Admin Portal
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
]
