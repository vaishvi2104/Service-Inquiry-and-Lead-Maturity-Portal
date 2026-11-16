"""
Business logic and service layer for admin dashboard.
Handles advanced metric aggregation, charts data, filtered queries,
Kanban grouping, follow-up management, and atomic status transitions.
"""
import csv
from typing import Tuple, Dict, Any, List
from datetime import datetime, timedelta
from django.utils import timezone
from django.http import HttpResponse
from django.db import transaction
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from inquiries.models import Inquiry, LeadStatus, ServiceChoices, LeadStatusHistory


def get_dashboard_metrics() -> Dict[str, Any]:
    """
    Compute dynamic database-backed inquiry counts and conversion analytics
    across all lead stages and follow-up schedules.
    """
    now = timezone.now()
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

    # Follow-ups due: scheduled <= now and not closed/mature
    follow_ups_due = Inquiry.objects.filter(
        follow_up_date__lte=now
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
        # Chart Data payloads
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

    # 1. Search text filter across name, mobile, reference ID, and email
    if search_query:
        cleaned = search_query.strip()[:100]
        queryset = queryset.filter(
            Q(full_name__icontains=cleaned) |
            Q(mobile_number__icontains=cleaned) |
            Q(reference_id__icontains=cleaned) |
            Q(email__icontains=cleaned)
        )

    # 2. Status filter
    valid_statuses = [choice[0] for choice in LeadStatus.choices]
    if status_filter and status_filter in valid_statuses:
        queryset = queryset.filter(status=status_filter)

    # 3. Service filter
    valid_services = [choice[0] for choice in ServiceChoices.choices]
    if service_filter and service_filter in valid_services:
        queryset = queryset.filter(service=service_filter)

    # 4. Date Range filters (YYYY-MM-DD)
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
        LeadStatus.NEW: 'bg-blue-lt',
        LeadStatus.CONTACTED: 'bg-azure-lt',
        LeadStatus.FOLLOW_UP: 'bg-yellow-lt',
        LeadStatus.PROPOSAL_SENT: 'bg-purple-lt',
        LeadStatus.MATURE: 'bg-green-lt',
        LeadStatus.CLOSED: 'bg-secondary-lt',
    }

    all_leads = Inquiry.objects.all().order_by('-updated_at')
    leads_by_stage = {}
    for stage_key, _ in LeadStatus.choices:
        leads_by_stage[stage_key] = []

    for lead in all_leads:
        if lead.status in leads_by_stage:
            leads_by_stage[lead.status].append(lead)

    for stage_key, stage_label in LeadStatus.choices:
        columns.append({
            'key': stage_key,
            'label': stage_label,
            'badge_class': badge_map.get(stage_key, 'bg-secondary-lt'),
            'leads': leads_by_stage[stage_key],
            'count': len(leads_by_stage[stage_key]),
        })

    return columns


def get_follow_ups_data() -> Dict[str, Any]:
    """
    Retrieve inquiries categorized into Overdue, Due Today, and Upcoming follow-ups.
    """
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    active_inquiries = Inquiry.objects.exclude(status__in=[LeadStatus.MATURE, LeadStatus.CLOSED])

    overdue = active_inquiries.filter(follow_up_date__lt=now).order_by('follow_up_date')
    due_today = active_inquiries.filter(follow_up_date__gte=today_start, follow_up_date__lt=today_end).order_by('follow_up_date')
    upcoming = active_inquiries.filter(follow_up_date__gte=today_end).order_by('follow_up_date')
    unscheduled = active_inquiries.filter(follow_up_date__isnull=True).order_by('-created_at')[:20]

    return {
        'overdue': overdue,
        'due_today': due_today,
        'upcoming': upcoming,
        'unscheduled': unscheduled,
        'total_due': overdue.count() + due_today.count(),
    }


def execute_status_transition(
    inquiry_id: int,
    new_status: str,
    acting_user,
    remarks: str = ''
) -> Tuple[bool, str, Inquiry | None]:
    """
    Atomically transition an inquiry's status stage and record the audit history.
    Locks row using select_for_update() to eliminate race conditions.
    Enforces documented policy: no-op updates (same status) are rejected.
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
    Stream a sanitized, formatted CSV file of lead records for reporting.
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
        writer.writerow([
            lead.reference_id,
            lead.full_name,
            lead.mobile_number,
            lead.email,
            lead.get_service_display(),
            lead.get_status_display(),
            lead.follow_up_date.strftime('%Y-%m-%d %H:%M') if lead.follow_up_date else 'Not Scheduled',
            lead.created_at.strftime('%Y-%m-%d %H:%M'),
            lead.updated_at.strftime('%Y-%m-%d %H:%M'),
            lead.message.replace('\n', ' ').strip(),
        ])

    return response
