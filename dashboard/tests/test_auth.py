"""
Authentication and authorization tests for staff dashboard.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from inquiries.models import Inquiry, ServiceChoices

User = get_user_model()


class DashboardAuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='staff_admin',
            password='StaffPassword123!',
            is_staff=True,
            is_active=True
        )
        self.regular_user = User.objects.create_user(
            username='regular_customer',
            password='CustomerPassword123!',
            is_staff=False,
            is_active=True
        )
        self.inquiry = Inquiry.objects.create(
            reference_id='SS-20261116-AUTH',
            full_name='Auth Test Lead',
            mobile_number='9876543210',
            email='auth@example.com',
            service=ServiceChoices.COMPANY_INCORPORATION,
        )

    def test_anonymous_access_to_overview_redirects_to_login(self):
        response = self.client.get(reverse('dashboard:overview'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('dashboard:login'), response.url)

    def test_anonymous_access_to_leads_redirects_to_login(self):
        response = self.client.get(reverse('dashboard:leads'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('dashboard:login'), response.url)

    def test_anonymous_access_to_lead_detail_redirects_to_login(self):
        response = self.client.get(reverse('dashboard:lead_detail', args=[self.inquiry.reference_id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('dashboard:login'), response.url)

    def test_anonymous_access_to_status_update_redirects_to_login(self):
        response = self.client.post(
            reverse('dashboard:lead_status_update', args=[self.inquiry.reference_id]),
            data={'new_status': 'contacted'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('dashboard:login'), response.url)

    def test_authenticated_non_staff_user_denied_forbidden(self):
        self.client.login(username='regular_customer', password='CustomerPassword123!')
        response = self.client.get(reverse('dashboard:overview'))
        self.assertEqual(response.status_code, 403)

    def test_valid_staff_login_succeeds(self):
        response = self.client.post(reverse('dashboard:login'), data={
            'username': 'staff_admin',
            'password': 'StaffPassword123!',
        })
        self.assertRedirects(response, reverse('dashboard:overview'))

    def test_invalid_login_fails_safely(self):
        response = self.client.post(reverse('dashboard:login'), data={
            'username': 'staff_admin',
            'password': 'WrongPassword!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password')

    def test_logout_via_get_method_rejected(self):
        self.client.login(username='staff_admin', password='StaffPassword123!')
        response = self.client.get(reverse('dashboard:logout'))
        # Must require POST
        self.assertEqual(response.status_code, 405)

    def test_logout_via_post_succeeds_and_invalidates_session(self):
        self.client.login(username='staff_admin', password='StaffPassword123!')
        response = self.client.post(reverse('dashboard:logout'))
        self.assertRedirects(response, reverse('dashboard:login'))

        # Subsquent access should redirect to login
        check_resp = self.client.get(reverse('dashboard:overview'))
        self.assertEqual(check_resp.status_code, 302)

    def test_no_public_admin_registration_endpoint(self):
        from django.urls import resolve, Resolver404
        # Verify common registration URLs don't resolve
        for path in ['/register/', '/dashboard/register/', '/signup/', '/dashboard/signup/']:
            with self.assertRaises(Resolver404):
                resolve(path)
