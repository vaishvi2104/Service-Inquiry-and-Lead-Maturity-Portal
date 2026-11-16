"""
Unit tests for InquirySubmissionForm validation and sanitization.
"""
from django.test import TestCase
from inquiries.forms import InquirySubmissionForm
from inquiries.models import ServiceChoices


class InquirySubmissionFormTests(TestCase):
    def test_valid_form_submission(self):
        form_data = {
            'full_name': 'Rohan K. Verma',
            'mobile_number': '9876543210',
            'email': 'rohan@example.com',
            'service': ServiceChoices.TRADEMARK_REGISTRATION,
            'message': 'Seeking trademark registration assistance for brand name.',
            'website_url': '',  # Honeypot empty
        }
        form = InquirySubmissionForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['full_name'], 'Rohan K. Verma')
        self.assertEqual(form.cleaned_data['mobile_number'], '9876543210')

    def test_blank_required_fields_rejected(self):
        form = InquirySubmissionForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('full_name', form.errors)
        self.assertIn('mobile_number', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('service', form.errors)

    def test_invalid_mobile_number_short(self):
        form = InquirySubmissionForm(data={
            'full_name': 'Rohan Verma',
            'mobile_number': '98765',  # Less than 10 digits
            'email': 'rohan@example.com',
            'service': ServiceChoices.COMPANY_INCORPORATION,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('mobile_number', form.errors)

    def test_invalid_mobile_number_with_country_code(self):
        form = InquirySubmissionForm(data={
            'full_name': 'Rohan Verma',
            'mobile_number': '+919876543210',  # Country code prefix not allowed in 10-digit input
            'email': 'rohan@example.com',
            'service': ServiceChoices.COMPANY_INCORPORATION,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('mobile_number', form.errors)

    def test_invalid_mobile_number_alphanumeric(self):
        form = InquirySubmissionForm(data={
            'full_name': 'Rohan Verma',
            'mobile_number': '98765abcde',  # Letters included
            'email': 'rohan@example.com',
            'service': ServiceChoices.COMPANY_INCORPORATION,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('mobile_number', form.errors)

    def test_invalid_email_format(self):
        form = InquirySubmissionForm(data={
            'full_name': 'Rohan Verma',
            'mobile_number': '9876543210',
            'email': 'not-an-email-address',
            'service': ServiceChoices.COMPANY_INCORPORATION,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_unknown_service_choice_rejected(self):
        form = InquirySubmissionForm(data={
            'full_name': 'Rohan Verma',
            'mobile_number': '9876543210',
            'email': 'rohan@example.com',
            'service': 'arbitrary_fake_service',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('service', form.errors)

    def test_overlong_message_rejected(self):
        form = InquirySubmissionForm(data={
            'full_name': 'Rohan Verma',
            'mobile_number': '9876543210',
            'email': 'rohan@example.com',
            'service': ServiceChoices.COMPANY_INCORPORATION,
            'message': 'A' * 2001,  # Max allowed is 2000
        })
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)

    def test_honeypot_filled_causes_rejection(self):
        form = InquirySubmissionForm(data={
            'full_name': 'Bot Submitter',
            'mobile_number': '9876543210',
            'email': 'bot@spammer.com',
            'service': ServiceChoices.COMPANY_INCORPORATION,
            'website_url': 'https://spam-link.com',  # Bot populated honeypot
        })
        self.assertFalse(form.is_valid())
        self.assertIn('website_url', form.errors)

    def test_name_whitespace_normalized(self):
        form = InquirySubmissionForm(data={
            'full_name': '   Priya    Nair   ',
            'mobile_number': '9876543210',
            'email': 'priya@example.com',
            'service': ServiceChoices.SEED_FUND_SUPPORT,
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['full_name'], 'Priya Nair')
