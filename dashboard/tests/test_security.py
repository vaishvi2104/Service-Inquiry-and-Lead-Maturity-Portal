"""
Security control verification tests: CSRF enforcement, HTTP method restrictions,
SQL injection resistance, and XSS output escaping.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from inquiries.models import Inquiry, ServiceChoices, LeadStatus

User = get_user_model()


class DashboardSecurityTests(TestCase):
    def setUp(self):
        # Client with CSRF enforcement active
        self.csrf_client = Client(enforce_csrf_checks=True)
        self.staff_user = User.objects.create_user(
            username='sec_admin',
            password='StaffPassword123!',
            is_staff=True,
            is_active=True
        )
        self.inquiry = Inquiry.objects.create(
            reference_id='SS-20261116-SEC1',
            full_name='Security Probe Lead',
            mobile_number='9876543210',
            email='sec@example.com',
            service=ServiceChoices.TRADEMARK_REGISTRATION,
            status=LeadStatus.NEW,
        )

    def test_csrf_protection_enforced_on_status_update(self):
        self.csrf_client.login(username='sec_admin', password='StaffPassword123!')
        url = reverse('dashboard:lead_status_update', args=[self.inquiry.reference_id])
        # POST without CSRF token must fail with 403 Forbidden
        response = self.csrf_client.post(url, data={'new_status': LeadStatus.CONTACTED})
        self.assertEqual(response.status_code, 403)

    def test_csrf_protection_enforced_on_logout(self):
        self.csrf_client.login(username='sec_admin', password='StaffPassword123!')
        url = reverse('dashboard:logout')
        # POST without CSRF token must fail with 403 Forbidden
        response = self.csrf_client.post(url)
        self.assertEqual(response.status_code, 403)

    def test_get_request_cannot_change_lead_status(self):
        client = Client()
        client.login(username='sec_admin', password='StaffPassword123!')
        url = reverse('dashboard:lead_status_update', args=[self.inquiry.reference_id])
        response = client.get(url, {'new_status': LeadStatus.CLOSED})
        # Must return 405 Method Not Allowed
        self.assertEqual(response.status_code, 405)
        self.inquiry.refresh_from_db()
        self.assertEqual(self.inquiry.status, LeadStatus.NEW)

    def test_sql_injection_probe_strings_handled_safely(self):
        client = Client()
        client.login(username='sec_admin', password='StaffPassword123!')
        sql_payloads = [
            "' OR 1=1 --",
            "'; DROP TABLE inquiries_inquiry; --",
            "1' UNION SELECT username, password FROM auth_user --",
            "admin'--",
            '" OR ""="',
        ]
        for payload in sql_payloads:
            response = client.get(reverse('dashboard:leads'), {'q': payload})
            # Query must execute cleanly without database syntax error or 500
            self.assertEqual(response.status_code, 200)

    def test_template_autoescaping_prevents_xss(self):
        client = Client()
        client.login(username='sec_admin', password='StaffPassword123!')
        malicious_inquiry = Inquiry.objects.create(
            reference_id='SS-20261116-XSS1',
            full_name='XSS Target',
            mobile_number='9876543210',
            email='xss@example.com',
            service=ServiceChoices.SEED_FUND_SUPPORT,
            message='<script>alert("PWNED")</script><img src="x" onerror="alert(1)">',
        )
        response = client.get(reverse('dashboard:lead_detail', args=[malicious_inquiry.reference_id]))
        self.assertEqual(response.status_code, 200)
        # Verify script tag is HTML-escaped and not rendered raw
        self.assertContains(response, '&lt;script&gt;alert(&quot;PWNED&quot;)&lt;/script&gt;')
        self.assertNotContains(response, '<script>alert("PWNED")</script>')

    def test_security_cookie_configurations(self):
        # Verify HTTPOnly and SameSite settings on sessions and CSRF
        self.assertTrue(settings.SESSION_COOKIE_HTTPONLY)
        self.assertTrue(settings.CSRF_COOKIE_HTTPONLY)
        self.assertEqual(settings.SESSION_COOKIE_SAMESITE, 'Lax')
        self.assertEqual(settings.CSRF_COOKIE_SAMESITE, 'Lax')
