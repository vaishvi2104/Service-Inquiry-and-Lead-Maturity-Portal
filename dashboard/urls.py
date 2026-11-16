"""
URL routes for the staff admin dashboard.
"""
from django.urls import path
from dashboard import views

app_name = 'dashboard'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.overview_view, name='overview'),
    path('leads/', views.leads_list_view, name='leads'),
    path('leads/<str:reference_id>/', views.lead_detail_view, name='lead_detail'),
    path('leads/<str:reference_id>/update-status/', views.lead_status_update_view, name='lead_status_update'),
]
