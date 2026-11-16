"""
Service layer for inquiries: reference ID generation, rate-limiting, and persistence.
"""
import secrets
from datetime import datetime
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from inquiries.models import Inquiry, LeadStatus, LeadStatusHistory


def generate_unique_reference_id(max_retries: int = 5) -> str:
    """
    Generate a collision-resistant, non-guessable inquiry reference ID.
    Format: SS-YYYYMMDD-XXXX where XXXX is a cryptographic hexadecimal token.
    Retries up to max_retries if a collision occurs.
    """
    date_prefix = datetime.now().strftime('%Y%m%d')
    for _ in range(max_retries):
        random_suffix = secrets.token_hex(2).upper()  # 4 characters
        candidate_id = f"SS-{date_prefix}-{random_suffix}"
        if not Inquiry.objects.filter(reference_id=candidate_id).exists():
            return candidate_id

    # Fallback to 8-character token if collision occurs repeatedly
    longer_suffix = secrets.token_hex(4).upper()
    return f"SS-{date_prefix}-{longer_suffix}"


def get_client_ip(request) -> str:
    """
    Extract client IP address safely from the request.
    Uses standard REMOTE_ADDR to avoid trusting spoofed HTTP headers
    unless explicitly configured behind a verified reverse proxy.
    """
    return request.META.get('REMOTE_ADDR', '127.0.0.1')


def check_rate_limit(request) -> bool:
    """
    Check if the client has exceeded the inquiry submission rate limit.
    Returns True if throttled (blocked), False if allowed.
    """
    ip = get_client_ip(request)
    cache_key = f"inquiry_throttle_{ip}"
    max_requests = getattr(settings, 'INQUIRY_RATE_LIMIT_MAX_REQUESTS', 5)
    window_seconds = getattr(settings, 'INQUIRY_RATE_LIMIT_WINDOW_SECONDS', 600)

    try:
        current_count = cache.get(cache_key, 0)
        if current_count >= max_requests:
            return True
        cache.set(cache_key, current_count + 1, timeout=window_seconds)
        return False
    except Exception:
        # If cache backend is unavailable, fail open safely
        return False


def save_customer_inquiry(cleaned_data: dict) -> Inquiry:
    """
    Atomically persist a validated customer inquiry and generate its initial audit record.
    """
    with transaction.atomic():
        ref_id = generate_unique_reference_id()
        inquiry = Inquiry.objects.create(
            reference_id=ref_id,
            full_name=cleaned_data['full_name'],
            mobile_number=cleaned_data['mobile_number'],
            email=cleaned_data['email'],
            service=cleaned_data['service'],
            message=cleaned_data.get('message', ''),
            status=LeadStatus.NEW,
        )
        # Create initial audit log entry
        LeadStatusHistory.objects.create(
            inquiry=inquiry,
            previous_status=LeadStatus.NEW,
            new_status=LeadStatus.NEW,
            updated_by=None,
            remarks='Initial customer inquiry submitted via public portal.',
        )
        return inquiry
