"""
Tests for strict ASCII mobile number validation and WhatsApp outreach link generation.
Verifies rejection of Devanagari numerals, Eastern Arabic numerals, and non-ASCII Unicode digits.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from inquiries.validators import validate_mobile_number
from inquiries.forms import InquirySubmissionForm
from inquiries.models import Inquiry, ServiceChoices, LeadStatus


class MobileNumberValidationTests(TestCase):
    def test_valid_ascii_10_digit_numbers_accepted(self):
        valid_numbers = [
            '9876543210',
            '6352675546',
            '7012345678',
            '8899001122',
        ]
        for num in valid_numbers:
            try:
                validate_mobile_number(num)
            except ValidationError:
                self.fail(f"validate_mobile_number raised ValidationError unexpectedly for valid number: {num}")

    def test_devanagari_numerals_strictly_rejected(self):
        # Devanagari digits: ९८७६५४३२१० (9876543210 in Hindi/Marathi/Sanskrit)
        devanagari_number = '९८७६५४३२१०'
        with self.assertRaises(ValidationError) as ctx:
            validate_mobile_number(devanagari_number)
        self.assertIn('only digits 0-9', str(ctx.exception))

    def test_mixed_devanagari_and_ascii_rejected(self):
        mixed_number = '98765४३२१०'
        with self.assertRaises(ValidationError):
            validate_mobile_number(mixed_number)

    def test_eastern_arabic_numerals_rejected(self):
        # Eastern Arabic digits: ٠١٢٣٤٥٦٧٨٩
        arabic_number = '٠١٢٣٤٥٦٧٨٩'
        with self.assertRaises(ValidationError):
            validate_mobile_number(arabic_number)

    def test_fullwidth_unicode_numerals_rejected(self):
        # Fullwidth digits: ０１２３４５６７８９
        fullwidth_number = '０１２３４５６７８９'
        with self.assertRaises(ValidationError):
            validate_mobile_number(fullwidth_number)

    def test_short_and_long_numbers_rejected(self):
        with self.assertRaises(ValidationError):
            validate_mobile_number('98765')
        with self.assertRaises(ValidationError):
            validate_mobile_number('98765432100')

    def test_form_validation_rejects_devanagari_number(self):
        form = InquirySubmissionForm(data={
            'full_name': 'Devanagari Test',
            'mobile_number': '९८७६५४३२१०',
            'email': 'devanagari@example.com',
            'service': ServiceChoices.COMPANY_INCORPORATION,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('mobile_number', form.errors)

    def test_whatsapp_url_rejects_non_ascii_digits(self):
        inquiry = Inquiry(
            reference_id='SS-20261117-TEST',
            full_name='Unicode Test',
            mobile_number='९८७६५४३२१०',
            email='uni@example.com',
            service=ServiceChoices.TRADEMARK_REGISTRATION,
        )
        # Non-ASCII digits must not result in a valid wa.me URL
        self.assertIsNone(inquiry.get_whatsapp_url())
