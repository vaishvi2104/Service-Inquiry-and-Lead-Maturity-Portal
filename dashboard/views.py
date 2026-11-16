"""
Views for staff lead management dashboard.
Implements secure role-based access control, CSRF enforcement, safe search/filtering,
dynamic analytics, and atomic lead stage updates.
"""
from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseNotAllowed, HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.utils.http import url_has_allowed_host_and_scheme
from inquiries.models import Inquiry, LeadStatus
from dashboard.forms import StaffLoginForm, LeadStatusUpdateForm
from dashboard.services import (
    get_dashboard_metrics,
    get_filtered_leads_queryset,
    paginate_queryset,
    execute_status_transition,
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


def login_view(request):
    """
    Staff login view with CSRF validation and rate-safe credentials checking.
    """
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


def logout_view(request):
    """
    Staff logout endpoint. Enforces POST method with CSRF validation.
    Flushes the active session and redirects to the login screen.
    """
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'], 'Logout requires a secure POST request.')

    auth_logout(request)
    messages.info(request, 'You have been successfully logged out.')
    return redirect('dashboard:login')


@staff_required
def overview_view(request):
    """
    Executive dashboard overview displaying dynamic aggregation metrics across
    all lead stages and recent inquiries.
    """
    metrics = get_dashboard_metrics()
    recent_leads = Inquiry.objects.all().order_by('-created_at')[:8]

    return render(request, 'dashboard/overview.html', {
        'metrics': metrics,
        'recent_leads': recent_leads,
    })


@staff_required
def leads_list_view(request):
    """
    Leads table with parameterized search, status filtering, and query-preserving pagination.
    """
    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    page_number = request.GET.get('page', 1)

    queryset = get_filtered_leads_queryset(search_query=search_query, status_filter=status_filter)
    leads_page = paginate_queryset(queryset, page_number=page_number, page_size=10)

    # Pass status choices for filter UI
    status_choices = LeadStatus.choices

    return render(request, 'dashboard/leads.html', {
        'leads': leads_page,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': status_choices,
        'total_results': queryset.count(),
    })


@staff_required
def lead_detail_view(request, reference_id: str):
    """
    Comprehensive inquiry detail view showing customer submitted data,
    WhatsApp contact link, and complete status change audit timeline.
    """
    inquiry = get_object_or_404(Inquiry, reference_id=reference_id)
    history_records = inquiry.status_history.all().select_related('updated_by').order_by('-created_at')
    update_form = LeadStatusUpdateForm(initial={'new_status': inquiry.status})
    whatsapp_url = inquiry.get_whatsapp_url()

    return render(request, 'dashboard/lead_detail.html', {
        'inquiry': inquiry,
        'history_records': history_records,
        'update_form': update_form,
        'whatsapp_url': whatsapp_url,
    })


@staff_required
def lead_status_update_view(request, reference_id: str):
    """
    Process atomic status update with CSRF validation and audit history recording.
    """
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'], 'Status updates require a secure POST request.')

    inquiry = get_object_or_404(Inquiry, reference_id=reference_id)
    form = LeadStatusUpdateForm(request.POST)

    if form.is_valid():
        new_status = form.cleaned_data['new_status']
        remarks = form.cleaned_data.get('remarks', '')

        success, msg, updated_inquiry = execute_status_transition(
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

    return redirect('dashboard:lead_detail', reference_id=inquiry.reference_id)
