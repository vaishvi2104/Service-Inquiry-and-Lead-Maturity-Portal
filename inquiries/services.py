"""
Service layer for inquiries: reference ID generation, rate-limiting, and persistence.
"""
import ipaddress
import logging
import secrets
from datetime import datetime
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from inquiries.models import Inquiry, LeadStatus, LeadStatusHistory

logger = logging.getLogger(__name__)


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


def is_valid_ip(ip_str: str) -> bool:
    """Check if the provided string is a syntactically valid IPv4 or IPv6 address."""
    if not ip_str or not isinstance(ip_str, str):
        return False
    try:
        ipaddress.ip_address(ip_str.strip())
        return True
    except ValueError:
        return False


def get_client_ip(request) -> str:
    """
    Extract client IP address safely and robustly.
    - If USE_X_FORWARDED_FOR is True, inspects HTTP_X_FORWARDED_FOR and validates
      each candidate IP address against ipaddress syntax rather than blindly trusting
      arbitrary client-supplied strings.
    - Falls back safely to standard REMOTE_ADDR.
    - If REMOTE_ADDR is missing or invalid, falls back safely to '127.0.0.1'.
    """
    if getattr(settings, 'USE_X_FORWARDED_FOR', False):
        forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
        if forwarded:
            candidates = [ip.strip() for ip in forwarded.split(',') if ip.strip()]
            for candidate in candidates:
                if is_valid_ip(candidate):
                    return candidate

    remote_addr = request.META.get('REMOTE_ADDR', '')
    if is_valid_ip(remote_addr):
        return remote_addr.strip()

    return '127.0.0.1'


def check_rate_limit(request, prefix: str = 'inquiry_throttle', max_requests: int | None = None, window_seconds: int | None = None) -> bool:
    """
    Check if the client has exceeded the rate limit.
    Returns True if throttled (blocked), False if allowed.
    Fails safely (open) if the shared cache backend is unavailable.
    """
    ip = get_client_ip(request)
    cache_key = f"{prefix}_{ip}"
    limit = max_requests if max_requests is not None else getattr(settings, 'INQUIRY_RATE_LIMIT_MAX_REQUESTS', 5)
    window = window_seconds if window_seconds is not None else getattr(settings, 'INQUIRY_RATE_LIMIT_WINDOW_SECONDS', 600)

    try:
        current_count = cache.get(cache_key, 0)
        if current_count >= limit:
            return True
        cache.set(cache_key, current_count + 1, timeout=window)
        return False
    except Exception as exc:
        logger.warning(
            "Shared rate-limiting cache backend unavailable: %s. Request permitted safely under fail-open policy.",
            exc
        )
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
