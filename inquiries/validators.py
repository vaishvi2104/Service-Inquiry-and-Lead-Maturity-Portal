"""
Custom validators for customer inquiry submissions.
Authoritative server-side validation enforcing clean data integrity.
"""
import re
from django.core.exceptions import ValidationError


# Indian 10-digit mobile number: exactly 10 ASCII digits
MOBILE_REGEX = re.compile(r'^\d{10}$')

# Name validation: allows alphabetic characters, spaces, dots, hyphens, and apostrophes
NAME_REGEX = re.compile(r"^[A-Za-z\s.\'-]+$")


def validate_mobile_number(value: str) -> None:
    """
    Validate that the mobile number consists of exactly 10 ASCII digits.
    Rejects country codes (+91), spaces, punctuation, and non-digit characters.
    """
    if not value or not isinstance(value, str):
        raise ValidationError('Mobile number is required.')

    normalized = value.strip()
    if not MOBILE_REGEX.match(normalized):
        raise ValidationError(
            'Enter a valid 10-digit mobile number without country codes, spaces, or symbols.'
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
