"""
Custom validators for customer inquiry submissions.
Authoritative server-side validation enforcing clean data integrity.
"""
import re
from django.core.exceptions import ValidationError


# Indian 10-digit mobile number: strictly 10 ASCII digits (0-9)
# Uses explicit [0-9] character class with ASCII flag to reject Devanagari and other Unicode numerals.
MOBILE_REGEX = re.compile(r'^[0-9]{10}$', re.ASCII)

# Name validation: allows alphabetic characters, spaces, dots, hyphens, and apostrophes
NAME_REGEX = re.compile(r"^[A-Za-z\s.\'-]+$")


def validate_mobile_number(value: str) -> None:
    """
    Validate that the mobile number consists of exactly 10 ASCII digits (0-9).
    Rejects country codes (+91), spaces, punctuation, Devanagari/Unicode numerals,
    and non-digit characters.
    """
    if not value or not isinstance(value, str):
        raise ValidationError('Mobile number is required.')

    normalized = value.strip()

    # Reject if non-ASCII digits are present (e.g., Devanagari numerals ०-९)
    if not normalized.isascii() or not MOBILE_REGEX.match(normalized):
        raise ValidationError(
            'Enter a valid 10-digit mobile number containing only digits 0-9 without country codes, spaces, or symbols.'
        )


def validate_full_name(value: str) -> None:
    """
    Validate that the customer's full name contains only valid name characters
    and does not contain malicious control characters or arbitrary symbols.
    """
    if not value or not isinstance(value, str):
        raise ValidationError('Full name is required.')

    normalized = ' '.join(value.strip().split())
    if len(normalized) < 2:
        raise ValidationError('Full name must be at least 2 characters long.')
    if len(normalized) > 120:
        raise ValidationError('Full name must not exceed 120 characters.')

    # Check for disallowed control characters
    for ch in normalized:
        if ord(ch) < 32 and ch not in ('\t', '\n', '\r'):
            raise ValidationError('Full name contains invalid control characters.')

    if not NAME_REGEX.match(normalized):
        raise ValidationError('Full name should only contain letters, spaces, hyphens, dots, or apostrophes.')
