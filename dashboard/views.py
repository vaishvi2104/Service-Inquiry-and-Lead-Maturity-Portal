"""
Views for Sahay LeadFlow Tabler Staff Management Dashboard.
Provides complete CRM capabilities: authentication, KPI analytics, Kanban pipeline,
lead lifecycle editing, follow-up desk, audit history, advanced search, and profile settings.
"""
from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseNotAllowed, HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils import timezone
from inquiries.models import Inquiry, LeadStatus, ServiceChoices, LeadStatusHistory
from inquiries.services import generate_unique_reference_id
from dashboard.forms import (
    StaffLoginForm,
    LeadStatusUpdateForm,
    LeadForm,
    FollowUpScheduleForm,
    AdminProfileForm,
)
from dashboard.services import (
    get_dashboard_metrics,
    get_filtered_leads_queryset,
    paginate_queryset,
    execute_status_transition,
    get_kanban_columns,
    get_follow_ups_data,
    export_leads_to_csv,
)


def staff_required(view_func):
    """
    Decorator enforcing that the user is logged in AND is an active staff/superuser.
    Anonymous users are redirected to login.
    Authenticated non-staff users receive an explicit HTTP 403 Forbidden response.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{redirect('dashboard:login').url}?next={request.path}")
        if not (request.user.is_active and (request.user.is_staff or request.user.is_superuser)):
            return HttpResponseForbidden(
                'Access Denied: Staff authorization is required to access the admin portal.'
            )
        return view_func(request, *args, **kwargs)
    return _wrapped_view


# 1. Admin Login
def login_view(request):
    """Staff login view styled with Tabler single-card layout."""
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return redirect('dashboard:overview')

    redirect_to = request.GET.get('next', request.POST.get('next', ''))

    if request.method == 'POST':
        form = StaffLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_staff or user.is_superuser:
                auth_login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                if redirect_to and url_has_allowed_host_and_scheme(
                    url=redirect_to,
                    allowed_hosts={request.get_host()},
                    require_https=request.is_secure()
                ):
                    return redirect(redirect_to)
                return redirect('dashboard:overview')
            else:
                messages.error(request, 'Your account does not possess staff privileges to access this portal.')
        else:
            messages.error(request, 'Invalid username or password. Please verify credentials.')
    else:
        form = StaffLoginForm(request)

    return render(request, 'dashboard/login.html', {
        'form': form,
        'next': redirect_to,
    })


# Logout
def logout_view(request):
    """Staff logout endpoint. Enforces POST method with CSRF validation."""
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'], 'Logout requires a secure POST request.')

    auth_logout(request)
    messages.info(request, 'You have been successfully logged out.')
    return redirect('dashboard:login')


# 2. Main Dashboard
@staff_required
def overview_view(request):
    """
    Main executive dashboard with Tabler KPI cards, ApexCharts visualizations,
    recent inquiries list, and upcoming follow-ups.
    """
    metrics = get_dashboard_metrics()
    recent_leads = Inquiry.objects.all().order_by('-created_at')[:8]
    follow_ups = get_follow_ups_data()

    return render(request, 'dashboard/overview.html', {
        'metrics': metrics,
        'recent_leads': recent_leads,
        'upcoming_follow_ups': follow_ups['due_today'][:5] or follow_ups['upcoming'][:5],
        'total_due_follow_ups': follow_ups['total_due'],
    })


# 3. All Inquiries / Leads Directory
@staff_required
def leads_list_view(request):
    """
    Comprehensive leads table with parameterized search, stage filter,
    service filter, date range filter, and query-preserving pagination.
    """
    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    service_filter = request.GET.get('service', '').strip()
    date_from = request.GET.get('from_date', '').strip()
    date_to = request.GET.get('to_date', '').strip()
    page_number = request.GET.get('page', 1)

    queryset = get_filtered_leads_queryset(
        search_query=search_query,
        status_filter=status_filter,
        service_filter=service_filter,
        date_from=date_from,
        date_to=date_to,
    )
    leads_page = paginate_queryset(queryset, page_number=page_number, page_size=12)

    return render(request, 'dashboard/leads.html', {
        'leads': leads_page,
        'search_query': search_query,
        'status_filter': status_filter,
        'service_filter': service_filter,
        'date_from': date_from,
        'date_to': date_to,
        'status_choices': LeadStatus.choices,
        'service_choices': ServiceChoices.choices,
        'total_results': queryset.count(),
    })


# 4. Lead Details
@staff_required
def lead_detail_view(request, reference_id: str):
    """Comprehensive lead profile, WhatsApp link, status update, and history timeline."""
    inquiry = get_object_or_404(Inquiry, reference_id=reference_id)
    history_records = inquiry.status_history.all().select_related('updated_by').order_by('-created_at')
    update_form = LeadStatusUpdateForm(initial={'new_status': inquiry.status})
    follow_up_form = FollowUpScheduleForm(initial={
        'follow_up_date': inquiry.follow_up_date.strftime('%Y-%m-%dT%H:%M') if inquiry.follow_up_date else ''
    })
    whatsapp_url = inquiry.get_whatsapp_url()

    return render(request, 'dashboard/lead_detail.html', {
        'inquiry': inquiry,
        'history_records': history_records,
        'update_form': update_form,
        'follow_up_form': follow_up_form,
        'whatsapp_url': whatsapp_url,
    })


# Lead Status Update Action
@staff_required
def lead_status_update_view(request, reference_id: str):
    """Atomic status update with CSRF validation and audit history recording."""
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'], 'Status updates require a secure POST request.')

    inquiry = get_object_or_404(Inquiry, reference_id=reference_id)
    form = LeadStatusUpdateForm(request.POST)

    if form.is_valid():
        new_status = form.cleaned_data['new_status']
        remarks = form.cleaned_data.get('remarks', '')

        success, msg, _ = execute_status_transition(
            inquiry_id=inquiry.id,
            new_status=new_status,
            acting_user=request.user,
            remarks=remarks,
        )
        if success:
            messages.success(request, msg)
        else:
            messages.warning(request, msg)
    else:
        messages.error(request, 'Invalid status update request. Please review the form.')

    # Redirect back to where requested (kanban or detail)
    redirect_target = request.POST.get('next_page', '')
    if redirect_target == 'kanban':
        return redirect('dashboard:kanban')
    return redirect('dashboard:lead_detail', reference_id=inquiry.reference_id)


# 5. Add New Lead
@staff_required
def lead_create_view(request):
    """Manually register a new lead received via phone, direct email, or offline inquiry."""
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.reference_id = generate_unique_reference_id()
            inquiry.assigned_to = request.user
            inquiry.save()

            # Record initial audit entry
            LeadStatusHistory.objects.create(
                inquiry=inquiry,
                previous_status=inquiry.status,
                new_status=inquiry.status,
                updated_by=request.user,
                remarks='Lead registered manually via staff portal.',
            )
            messages.success(request, f'New lead {inquiry.reference_id} created successfully.')
            return redirect('dashboard:lead_detail', reference_id=inquiry.reference_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LeadForm(initial={'status': LeadStatus.NEW})

    return render(request, 'dashboard/lead_form.html', {
        'form': form,
        'title': 'Register New Lead',
        'is_edit': False,
    })


# Edit Lead
@staff_required
def lead_edit_view(request, reference_id: str):
    """Edit customer details and internal notes for an existing lead."""
    inquiry = get_object_or_404(Inquiry, reference_id=reference_id)

    if request.method == 'POST':
        form = LeadForm(request.POST, instance=inquiry)
        if form.is_valid():
            old_status = inquiry.status
            updated_inquiry = form.save()

            # If status was modified during edit, record history
            if updated_inquiry.status != old_status:
                LeadStatusHistory.objects.create(
                    inquiry=updated_inquiry,
                    previous_status=old_status,
                    new_status=updated_inquiry.status,
                    updated_by=request.user,
                    remarks='Stage updated via lead edit form.',
                )

            messages.success(request, f'Lead {inquiry.reference_id} updated successfully.')
            return redirect('dashboard:lead_detail', reference_id=inquiry.reference_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LeadForm(instance=inquiry)

    return render(request, 'dashboard/lead_form.html', {
        'form': form,
        'inquiry': inquiry,
        'title': f'Edit Lead {inquiry.reference_id}',
        'is_edit': True,
    })


# 6. Lead Pipeline / Kanban
@staff_required
def lead_kanban_view(request):
    """Visual Kanban board showing leads across all 6 maturity stages."""
    columns = get_kanban_columns()
    status_choices = LeadStatus.choices

    return render(request, 'dashboard/kanban.html', {
        'columns': columns,
        'status_choices': status_choices,
        'total_leads': Inquiry.objects.count(),
    })


# Quick Kanban Stage Move
@staff_required
def lead_kanban_move_view(request, reference_id: str):
    """Quickly move a lead to a new stage from the Kanban board."""
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    inquiry = get_object_or_404(Inquiry, reference_id=reference_id)
    target_stage = request.POST.get('target_stage', '').strip()
    remarks = request.POST.get('remarks', 'Stage updated from Kanban board.').strip()

    success, msg, _ = execute_status_transition(
        inquiry_id=inquiry.id,
        new_status=target_stage,
        acting_user=request.user,
        remarks=remarks,
    )
    if success:
        messages.success(request, msg)
    else:
        messages.warning(request, msg)

    return redirect('dashboard:kanban')


# 7. Follow-up Management
@staff_required
def follow_ups_view(request):
    """Dedicated follow-up management desk with Overdue, Due Today, and Upcoming lists."""
    follow_ups = get_follow_ups_data()
    return render(request, 'dashboard/follow_ups.html', {
        'follow_ups': follow_ups,
    })


# Schedule Follow-up Action
@staff_required
def schedule_follow_up_view(request, reference_id: str):
    """Schedule or modify follow-up date and remarks for a lead."""
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    inquiry = get_object_or_404(Inquiry, reference_id=reference_id)
    form = FollowUpScheduleForm(request.POST)

    if form.is_valid():
        inquiry.follow_up_date = form.cleaned_data['follow_up_date']
        inquiry.save(update_fields=['follow_up_date', 'updated_at'])

        remarks = form.cleaned_data.get('remarks', '')
        if remarks:
            inquiry.internal_notes = (
                f"[{timezone.now().strftime('%Y-%m-%d %H:%M')}] Follow-up note: {remarks}\n"
                f"{inquiry.internal_notes}"
            )[:2000]
            inquiry.save(update_fields=['internal_notes'])

        messages.success(request, f'Follow-up scheduled for {inquiry.reference_id} on {inquiry.follow_up_date.strftime("%d %b %Y, %I:%M %p")}.')
    else:
        messages.error(request, 'Invalid date/time provided for follow-up schedule.')

    redirect_to = request.POST.get('next', '')
    if redirect_to == 'follow_ups':
        return redirect('dashboard:follow_ups')
    return redirect('dashboard:lead_detail', reference_id=inquiry.reference_id)


# 8. Lead Status History
@staff_required
def status_history_view(request):
    """Organizational audit trail tracking all status transitions across all leads."""
    history_records = LeadStatusHistory.objects.all().select_related('inquiry', 'updated_by').order_by('-created_at')

    ref_filter = request.GET.get('ref', '').strip()
    if ref_filter:
        history_records = history_records.filter(inquiry__reference_id__icontains=ref_filter)

    user_filter = request.GET.get('user', '').strip()
    if user_filter:
        history_records = history_records.filter(updated_by__username__icontains=user_filter)

    paginated_history = paginate_queryset(history_records, request.GET.get('page', 1), page_size=15)

    return render(request, 'dashboard/status_history.html', {
        'history_records': paginated_history,
        'ref_filter': ref_filter,
        'user_filter': user_filter,
        'total_count': history_records.count(),
    })


# 9. Search and Advanced Filters
@staff_required
def advanced_search_view(request):
    """Advanced search page supporting multi-field filtering and report generation."""
    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    service_filter = request.GET.get('service', '').strip()
    date_from = request.GET.get('from_date', '').strip()
    date_to = request.GET.get('to_date', '').strip()

    has_filters = any([search_query, status_filter, service_filter, date_from, date_to])
    queryset = get_filtered_leads_queryset(
        search_query=search_query,
        status_filter=status_filter,
        service_filter=service_filter,
        date_from=date_from,
        date_to=date_to,
    )
    leads_page = paginate_queryset(queryset, request.GET.get('page', 1), page_size=15)

    return render(request, 'dashboard/advanced_search.html', {
        'leads': leads_page,
        'search_query': search_query,
        'status_filter': status_filter,
        'service_filter': service_filter,
        'date_from': date_from,
        'date_to': date_to,
        'status_choices': LeadStatus.choices,
        'service_choices': ServiceChoices.choices,
        'has_filters': has_filters,
        'total_results': queryset.count(),
    })


# Export to CSV
@staff_required
def export_leads_csv_view(request):
    """Export filtered leads to a clean CSV file."""
    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    service_filter = request.GET.get('service', '').strip()
    date_from = request.GET.get('from_date', '').strip()
    date_to = request.GET.get('to_date', '').strip()

    queryset = get_filtered_leads_queryset(
        search_query=search_query,
        status_filter=status_filter,
        service_filter=service_filter,
        date_from=date_from,
        date_to=date_to,
    )
    return export_leads_to_csv(queryset)


# 10. Admin Profile and Settings
@staff_required
def profile_view(request):
    """Staff user profile details, credentials change, and system configuration."""
    user = request.user
    profile_form = AdminProfileForm(instance=user)
    password_form = PasswordChangeForm(user=user)

    if request.method == 'POST':
        action = request.POST.get('action', '')
        if action == 'update_profile':
            profile_form = AdminProfileForm(request.POST, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profile details updated successfully.')
                return redirect('dashboard:profile')
            else:
                messages.error(request, 'Error updating profile details.')
        elif action == 'change_password':
            password_form = PasswordChangeForm(user=user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password changed successfully.')
                return redirect('dashboard:profile')
            else:
                messages.error(request, 'Please correct the password errors below.')

    return render(request, 'dashboard/profile.html', {
        'profile_form': profile_form,
        'password_form': password_form,
        'user_obj': user,
    })
