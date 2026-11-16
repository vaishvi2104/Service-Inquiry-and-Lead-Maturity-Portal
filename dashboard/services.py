"""
Business logic and service layer for admin dashboard.
Handles metric aggregation, secure filtered queries, and atomic status transitions.
"""
from typing import Tuple, Dict, Any
from django.db import transaction
from django.db.models import Count, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from inquiries.models import Inquiry, LeadStatus, LeadStatusHistory


def get_dashboard_metrics() -> Dict[str, int]:
    """
    Compute dynamic database-backed inquiry counts across all lead stages.
    Uses efficient aggregation.
    """
    status_counts = Inquiry.objects.values('status').annotate(total=Count('id'))
    counts_map = {item['status']: item['total'] for item in status_counts}

    total_inquiries = Inquiry.objects.count()

    return {
        'total': total_inquiries,
        'new': counts_map.get(LeadStatus.NEW, 0),
        'contacted': counts_map.get(LeadStatus.CONTACTED, 0),
        'follow_up': counts_map.get(LeadStatus.FOLLOW_UP, 0),
        'proposal_sent': counts_map.get(LeadStatus.PROPOSAL_SENT, 0),
        'mature': counts_map.get(LeadStatus.MATURE, 0),
        'closed': counts_map.get(LeadStatus.CLOSED, 0),
    }


def get_filtered_leads_queryset(search_query: str = '', status_filter: str = ''):
    """
    Build a safe, parameterized Django ORM query combining search and status filter.
    Protects against SQL injection and rejects unknown status filter values.
    """
    queryset = Inquiry.objects.all().order_by('-created_at')

    # Apply search filter across name, mobile number, and reference ID
    if search_query:
        cleaned_search = search_query.strip()
        if len(cleaned_search) > 100:
            cleaned_search = cleaned_search[:100]
        queryset = queryset.filter(
            Q(full_name__icontains=cleaned_search) |
            Q(mobile_number__icontains=cleaned_search) |
            Q(reference_id__icontains=cleaned_search)
        )

    # Apply status filter
    valid_statuses = [choice[0] for choice in LeadStatus.choices]
    if status_filter and status_filter in valid_statuses:
        queryset = queryset.filter(status=status_filter)

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
