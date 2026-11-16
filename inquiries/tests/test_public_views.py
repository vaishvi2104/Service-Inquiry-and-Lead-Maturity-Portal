"""
Integration tests for public views and inquiry submission flow.
"""
from django.test import TestCase, Client
from django.urls import reverse
from inquiries.models import Inquiry, ServiceChoices, LeadStatus


class PublicViewsTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_homepage_loads(self):
        response = self.client.get(reverse('public:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Start-Up Sahay')
        self.assertContains(response, 'Guiding Indian Entrepreneurs')

    def test_all_four_required_services_present(self):
        response = self.client.get(reverse('public:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Company Incorporation')
        self.assertContains(response, 'Startup India DPIIT Recognition')
        self.assertContains(response, 'Trademark Registration')
        self.assertContains(response, 'Seed Fund Support')

    def test_disclaimer_rendered(self):
        response = self.client.get(reverse('public:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'not affiliated with')
        self.assertContains(response, 'Statutory Notice')

    def test_valid_inquiry_submission_persists_and_redirects(self):
        payload = {
            'full_name': 'Meera Sen',
            'mobile_number': '9876543210',
            'email': 'meera@example.com',
            'service': ServiceChoices.COMPANY_INCORPORATION,
            'message': 'Looking for Pvt Ltd registration guidance.',
            'website_url': '',
        }
        response = self.client.post(reverse('public:home'), data=payload)
        # Verify Post/Redirect/Get
        self.assertRedirects(response, reverse('public:success'))

        # Verify DB persistence
        inquiry = Inquiry.objects.filter(email='meera@example.com').first()
        self.assertIsNotNone(inquiry)
        self.assertEqual(inquiry.full_name, 'Meera Sen')
        self.assertEqual(inquiry.mobile_number, '9876543210')
        self.assertEqual(inquiry.status, LeadStatus.NEW)
        self.assertTrue(inquiry.reference_id.startswith('SS-'))

        # Verify initial audit history was created atomically
        self.assertEqual(inquiry.status_history.count(), 1)
        history = inquiry.status_history.first()
        self.assertEqual(history.new_status, LeadStatus.NEW)

    def test_success_page_displays_reference_id(self):
        inquiry = Inquiry.objects.create(
            reference_id='SS-20261116-TEST',
            full_name='Test Lead',
            mobile_number='9876543210',
            email='test@example.com',
            service=ServiceChoices.SEED_FUND_SUPPORT,
        )
        session = self.client.session
        session['inquiry_success_ref'] = inquiry.reference_id
        session['inquiry_success_service'] = inquiry.get_service_display()
        session.save()

        response = self.client.get(reverse('public:success'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SS-20261116-TEST')
        self.assertContains(response, 'Seed Fund Support')

    def test_success_page_direct_access_without_session_redirects(self):
        response = self.client.get(reverse('public:success'))
        self.assertRedirects(response, reverse('public:home'))

    def test_honeypot_submission_does_not_create_inquiry(self):
        initial_count = Inquiry.objects.count()
        payload = {
            'full_name': 'Bot Submitter',
            'mobile_number': '9876543210',
            'email': 'bot@example.com',
            'service': ServiceChoices.DPIIT_RECOGNITION,
            'website_url': 'http://spamsite.xyz',
        }
        response = self.client.post(reverse('public:home'), data=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Inquiry.objects.count(), initial_count)

    def test_xss_in_message_is_escaped(self):
        payload = {
            'full_name': 'Hacker <script>alert(1)</script>',
            'mobile_number': '9876543210',
            'email': 'hacker@example.com',
            'service': ServiceChoices.TRADEMARK_REGISTRATION,
            'message': '<script>alert("XSS Attack")</script><b>Bold inquiry</b>',
        }
        response = self.client.post(reverse('public:home'), data=payload)
        # Should be rejected because name validator detects disallowed symbols '<' and '>'
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Full name should only contain letters')
