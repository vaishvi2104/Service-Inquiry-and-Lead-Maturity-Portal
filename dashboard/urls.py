"""
URL routes for the Sahay LeadFlow Tabler staff admin dashboard.
"""
from django.urls import path
from dashboard import views

app_name = 'dashboard'

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # 1. Main Dashboard
    path('', views.overview_view, name='overview'),

    # 2. All Inquiries / Leads Directory
    path('leads/', views.leads_list_view, name='leads'),
    path('leads/create/', views.lead_create_view, name='lead_create'),
    path('leads/<str:reference_id>/', views.lead_detail_view, name='lead_detail'),
    path('leads/<str:reference_id>/edit/', views.lead_edit_view, name='lead_edit'),
    path('leads/<str:reference_id>/update-status/', views.lead_status_update_view, name='lead_status_update'),
    path('leads/<str:reference_id>/schedule-follow-up/', views.schedule_follow_up_view, name='schedule_follow_up'),

    # 3. Pipeline / Kanban
    path('kanban/', views.lead_kanban_view, name='kanban'),
    path('kanban/<str:reference_id>/move/', views.lead_kanban_move_view, name='kanban_move'),

    # 4. Follow-up Management
    path('follow-ups/', views.follow_ups_view, name='follow_ups'),

    # 5. Lead Status History (Audit Log)
    path('history/', views.status_history_view, name='status_history'),

    # 6. Search and Advanced Filters & CSV Export
    path('search/', views.advanced_search_view, name='advanced_search'),
    path('export/csv/', views.export_leads_csv_view, name='export_csv'),

    # 7. Admin Profile and Settings
    path('profile/', views.profile_view, name='profile'),
]
