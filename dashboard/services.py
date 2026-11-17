"""
Business logic and service layer for admin dashboard.
Handles advanced metric aggregation, charts data, filtered queries,
Kanban grouping, follow-up management, atomic status transitions,
CSV formula injection protection, and login rate limiting.
"""
import csv
import logging
from typing import Tuple, Dict, Any, List
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from django.http import HttpResponse
from django.db import transaction
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from inquiries.models import Inquiry, LeadStatus, ServiceChoices, LeadStatusHistory

logger = logging.getLogger(__name__)

# Dangerous trigger characters for CSV / spreadsheet formula injection
DANGEROUS_CSV_PREFIXES = ('=', '+', '-', '@', '\t', '\r', '|', '%')

# Strict allowed status transitions state machine
ALLOWED_STATUS_TRANSITIONS: Dict[str, set[str]] = {
    LeadStatus.NEW: {
        LeadStatus.CONTACTED,
        LeadStatus.FOLLOW_UP,
        LeadStatus.PROPOSAL_SENT,
        LeadStatus.MATURE,
        LeadStatus.CLOSED,
    },
    LeadStatus.CONTACTED: {
        LeadStatus.FOLLOW_UP,
        LeadStatus.PROPOSAL_SENT,
        LeadStatus.MATURE,
        LeadStatus.CLOSED,
    },
    LeadStatus.FOLLOW_UP: {
        LeadStatus.CONTACTED,
        LeadStatus.PROPOSAL_SENT,
        LeadStatus.MATURE,
        LeadStatus.CLOSED,
    },
    LeadStatus.PROPOSAL_SENT: {
        LeadStatus.FOLLOW_UP,
        LeadStatus.MATURE,
        LeadStatus.CLOSED,
    },
    LeadStatus.MATURE: {
        LeadStatus.FOLLOW_UP,
        LeadStatus.CLOSED,
    },
    LeadStatus.CLOSED: {
        LeadStatus.CONTACTED,
        LeadStatus.FOLLOW_UP,
    },
}


def sanitize_csv_value(val: Any) -> str:
    """
    Sanitize cell content to protect against spreadsheet formula injection (CSV Injection).
    If the stripped value starts with any dangerous character (=, +, -, @, tab, CR, pipe, %),
    prepends a single quote so spreadsheet engines interpret it strictly as plain text.
    Preserves clean formatting for standard values.
    """
    if val is None:
        return ''
    s = str(val)
    stripped = s.lstrip()
    if stripped and stripped[0] in DANGEROUS_CSV_PREFIXES:
        return f"'{s}"
    return s


def get_dashboard_metrics() -> Dict[str, Any]:
    """
    Compute dynamic database-backed inquiry counts and conversion analytics
    across all lead stages and follow-up schedules.
    Uses application timezone (Asia/Kolkata) to ensure consistent date boundaries.
    """
    now = timezone.now()
    tz = timezone.get_current_timezone()
    now_local = now.astimezone(tz)
    today_date = now_local.date()
    start_of_tomorrow = datetime.combine(today_date, datetime.min.time(), tzinfo=tz) + timedelta(days=1)

    status_counts = Inquiry.objects.values('status').annotate(total=Count('id'))
    counts_map = {item['status']: item['total'] for item in status_counts}

    total_inquiries = Inquiry.objects.count()
    new_count = counts_map.get(LeadStatus.NEW, 0)
    contacted_count = counts_map.get(LeadStatus.CONTACTED, 0)
    follow_up_count = counts_map.get(LeadStatus.FOLLOW_UP, 0)
    proposal_count = counts_map.get(LeadStatus.PROPOSAL_SENT, 0)
    mature_count = counts_map.get(LeadStatus.MATURE, 0)
    closed_count = counts_map.get(LeadStatus.CLOSED, 0)

    # Conversion rate: Mature leads / Total inquiries
    conversion_rate = round((mature_count / total_inquiries * 100), 1) if total_inquiries > 0 else 0.0

    # Follow-ups due: scheduled before end of today (Asia/Kolkata) and not closed/mature
    follow_ups_due = Inquiry.objects.filter(
        follow_up_date__lt=start_of_tomorrow
    ).exclude(status__in=[LeadStatus.MATURE, LeadStatus.CLOSED]).count()

    # Stage distribution for ApexCharts Donut
    stage_labels = [label for _, label in LeadStatus.choices]
    stage_series = [counts_map.get(key, 0) for key, _ in LeadStatus.choices]

    # Service-wise distribution for ApexCharts Bar
    service_counts = Inquiry.objects.values('service').annotate(total=Count('id'))
    service_map = {item['service']: item['total'] for item in service_counts}
    service_labels = [label for _, label in ServiceChoices.choices]
    service_series = [service_map.get(key, 0) for key, _ in ServiceChoices.choices]

    # Monthly trends (last 6 months)
    six_months_ago = now - timedelta(days=180)
    monthly_data = (
        Inquiry.objects.filter(created_at__gte=six_months_ago)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Count('id'))
        .order_by('month')
    )
    month_labels = [item['month'].strftime('%b %Y') for item in monthly_data] if monthly_data else [now.strftime('%b %Y')]
    month_series = [item['total'] for item in monthly_data] if monthly_data else [total_inquiries]

    return {
        'total': total_inquiries,
        'new': new_count,
        'contacted': contacted_count,
        'follow_up': follow_up_count,
        'follow_ups_due': follow_ups_due,
        'proposal_sent': proposal_count,
        'mature': mature_count,
        'closed': closed_count,
        'conversion_rate': conversion_rate,
        'stage_labels': stage_labels,
        'stage_series': stage_series,
        'service_labels': service_labels,
        'service_series': service_series,
        'service_breakdown': [{'service_label': l, 'count': c} for l, c in zip(service_labels, service_series)],
        'month_labels': month_labels,
        'month_series': month_series,
    }


def get_filtered_leads_queryset(
    search_query: str = '',
    status_filter: str = '',
    service_filter: str = '',
    date_from: str = '',
    date_to: str = ''
):
    """
    Build a safe, parameterized Django ORM query combining search, status,
    service, and date range filters.
    """
    queryset = Inquiry.objects.all().order_by('-created_at')

    if search_query:
        cleaned = search_query.strip()[:100]
        queryset = queryset.filter(
            Q(full_name__icontains=cleaned) |
            Q(mobile_number__icontains=cleaned) |
            Q(reference_id__icontains=cleaned) |
            Q(email__icontains=cleaned)
        )

    valid_statuses = [choice[0] for choice in LeadStatus.choices]
    if status_filter and status_filter in valid_statuses:
        queryset = queryset.filter(status=status_filter)

    valid_services = [choice[0] for choice in ServiceChoices.choices]
    if service_filter and service_filter in valid_services:
        queryset = queryset.filter(service=service_filter)

    if date_from:
        try:
            d_from = datetime.strptime(date_from.strip(), '%Y-%m-%d')
            queryset = queryset.filter(created_at__date__gte=d_from.date())
        except ValueError:
            pass

    if date_to:
        try:
            d_to = datetime.strptime(date_to.strip(), '%Y-%m-%d')
            queryset = queryset.filter(created_at__date__lte=d_to.date())
        except ValueError:
            pass

    return queryset


def paginate_queryset(queryset, page_number: int | str, page_size: int = 10):
    """
    Safely paginate a queryset, handling invalid or out-of-range page numbers.
    """
    paginator = Paginator(queryset, page_size)
    try:
        return paginator.page(page_number)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages if paginator.num_pages > 0 else 1)


def get_kanban_columns() -> List[Dict[str, Any]]:
    """
    Group all active inquiries by the six pipeline stages for the Kanban view.
    """
    columns = []
    badge_map = {
        LeadStatus.NEW: 'badge-new',
        LeadStatus.CONTACTED: 'badge-contacted',
        LeadStatus.FOLLOW_UP: 'badge-followup',
        LeadStatus.PROPOSAL_SENT: 'badge-proposal',
        LeadStatus.MATURE: 'badge-mature',
        LeadStatus.CLOSED: 'badge-closed',
    }

    all_leads = Inquiry.objects.all().order_by('-updated_at')
    leads_by_stage = {stage_key: [] for stage_key, _ in LeadStatus.choices}

    for lead in all_leads:
        if lead.status in leads_by_stage:
            leads_by_stage[lead.status].append(lead)

    for stage_key, stage_label in LeadStatus.choices:
        columns.append({
            'key': stage_key,
            'label': stage_label,
            'badge_class': badge_map.get(stage_key, 'badge-closed'),
            'leads': leads_by_stage[stage_key],
            'count': len(leads_by_stage[stage_key]),
        })

    return columns


def get_follow_ups_data() -> Dict[str, Any]:
    """
    Retrieve inquiries categorized into Overdue, Due Today, and Upcoming follow-ups.
    Uses configured application timezone (Asia/Kolkata) to compute midnight boundaries:
    - Overdue: follow-up date strictly earlier than today's local midnight (< start_of_today).
    - Due Today: follow-up date within today (>= start_of_today and < start_of_tomorrow).
    - Upcoming: follow-up date tomorrow or later (>= start_of_tomorrow).
    Overdue and Due Today are mutually exclusive; total_due represents unique total count.
    """
    tz = timezone.get_current_timezone()
    now_local = timezone.now().astimezone(tz)
    today_date = now_local.date()

    start_of_today = datetime.combine(today_date, datetime.min.time(), tzinfo=tz)
    start_of_tomorrow = start_of_today + timedelta(days=1)

    active_inquiries = Inquiry.objects.exclude(status__in=[LeadStatus.MATURE, LeadStatus.CLOSED])

    overdue = active_inquiries.filter(follow_up_date__lt=start_of_today).order_by('follow_up_date')
    due_today = active_inquiries.filter(
        follow_up_date__gte=start_of_today,
        follow_up_date__lt=start_of_tomorrow
    ).order_by('follow_up_date')
    upcoming = active_inquiries.filter(follow_up_date__gte=start_of_tomorrow).order_by('follow_up_date')
    unscheduled = active_inquiries.filter(follow_up_date__isnull=True).order_by('-created_at')[:20]

    return {
        'overdue': overdue,
        'due_today': due_today,
        'upcoming': upcoming,
        'unscheduled': unscheduled,
        'total_due': overdue.count() + due_today.count(),
    }


def is_valid_status_transition(current_status: str, target_status: str) -> bool:
    """Validate whether transitioning from current_status to target_status is allowed."""
    if current_status == target_status:
        return False
    allowed = ALLOWED_STATUS_TRANSITIONS.get(current_status, set())
    return target_status in allowed


def execute_status_transition(
    inquiry_id: int,
    new_status: str,
    acting_user,
    remarks: str = ''
) -> Tuple[bool, str, Inquiry | None]:
    """
    Centralized, atomic status transition service.
    Locks inquiry row with select_for_update() to prevent concurrent race conditions.
    Validates allowed state machine transitions, rejects no-ops, and creates audit history.
    """
    valid_statuses = [choice[0] for choice in LeadStatus.choices]
    if new_status not in valid_statuses:
        return False, 'Invalid status selection.', None

    with transaction.atomic():
        try:
            inquiry = Inquiry.objects.select_for_update().get(id=inquiry_id)
        except Inquiry.DoesNotExist:
            return False, 'Inquiry record not found.', None

        # Check for no-op update
        if inquiry.status == new_status:
            return False, f'Inquiry is already in "{inquiry.get_status_display()}" status. No changes made.', inquiry

        # Check state machine rules
        if not is_valid_status_transition(inquiry.status, new_status):
            target_label = dict(LeadStatus.choices).get(new_status, new_status)
            return False, f'Cannot transition lead from "{inquiry.get_status_display()}" to "{target_label}".', inquiry

        previous_status = inquiry.status
        inquiry.status = new_status
        inquiry.save(update_fields=['status', 'updated_at'])

        LeadStatusHistory.objects.create(
            inquiry=inquiry,
            previous_status=previous_status,
            new_status=new_status,
            updated_by=acting_user if acting_user and acting_user.is_authenticated else None,
            remarks=remarks.strip(),
        )

        return True, f'Status successfully updated to "{inquiry.get_status_display()}".', inquiry


def export_leads_to_csv(queryset) -> HttpResponse:
    """
    Stream a sanitized, formatted CSV file of lead records protected against formula injection.
    """
    response = HttpResponse(content_type='text/csv')
    timestamp = timezone.now().strftime('%Y%m%d_%H%M')
    response['Content-Disposition'] = f'attachment; filename="sahay_leads_{timestamp}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Reference ID',
        'Customer Name',
        'Mobile Number',
        'Email Address',
        'Service',
        'Current Stage',
        'Follow-up Date',
        'Created At',
        'Updated At',
        'Customer Message',
    ])

    for lead in queryset:
        follow_up_str = lead.follow_up_date.strftime('%Y-%m-%d %H:%M') if lead.follow_up_date else 'Not Scheduled'
        writer.writerow([
            sanitize_csv_value(lead.reference_id),
            sanitize_csv_value(lead.full_name),
            sanitize_csv_value(lead.mobile_number),
            sanitize_csv_value(lead.email),
            sanitize_csv_value(lead.get_service_display()),
            sanitize_csv_value(lead.get_status_display()),
            sanitize_csv_value(follow_up_str),
            sanitize_csv_value(lead.created_at.strftime('%Y-%m-%d %H:%M')),
            sanitize_csv_value(lead.updated_at.strftime('%Y-%m-%d %H:%M')),
            sanitize_csv_value(lead.message.replace('\n', ' ').strip()),
        ])

    return response


# Login Brute-Force & Lockout Helpers
def _get_login_cache_key(prefix: str, identifier: str) -> str:
    return f"login_fail_{prefix}_{identifier.strip().lower()}"


def is_login_locked(ip: str, username: str = '') -> bool:
    """Check if either IP or username is currently throttled / locked out."""
    limit = getattr(settings, 'LOGIN_MAX_ATTEMPTS', 5)
    ip_key = _get_login_cache_key('ip', ip)
    try:
        if cache.get(ip_key, 0) >= limit:
            return True
        if username:
            user_key = _get_login_cache_key('user', username)
            if cache.get(user_key, 0) >= limit:
                return True
    except Exception as exc:
        logger.warning("Cache backend error during login lockout check: %s", exc)
    return False


def record_login_failure(ip: str, username: str = '') -> int:
    """Increment failure counters for IP and username upon failed authentication."""
    lockout_seconds = getattr(settings, 'LOGIN_LOCKOUT_SECONDS', 300)
    max_count = 0
    try:
        ip_key = _get_login_cache_key('ip', ip)
        ip_count = cache.get(ip_key, 0) + 1
        cache.set(ip_key, ip_count, timeout=lockout_seconds)
        max_count = max(max_count, ip_count)

        if username:
            user_key = _get_login_cache_key('user', username)
            user_count = cache.get(user_key, 0) + 1
            cache.set(user_key, user_count, timeout=lockout_seconds)
            max_count = max(max_count, user_count)

        logger.warning(
            "Failed login attempt from IP '%s' for username '%s'. Recorded fail count: %d",
            ip, username, max_count
        )
    except Exception as exc:
        logger.warning("Cache backend error recording login failure: %s", exc)
    return max_count


def reset_login_failures(ip: str, username: str = '') -> None:
    """Clear failed login counters upon successful authentication."""
    try:
        cache.delete(_get_login_cache_key('ip', ip))
        if username:
            cache.delete(_get_login_cache_key('user', username))
    except Exception as exc:
        logger.warning("Cache backend error resetting login failures: %s", exc)
