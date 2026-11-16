"""
URL routes for the public customer portal.
"""
from django.urls import path
from inquiries import views

app_name = 'public'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('inquiry/success/', views.inquiry_success_view, name='success'),
]
