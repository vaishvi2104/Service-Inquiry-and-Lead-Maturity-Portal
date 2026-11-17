"""
Unit and integration tests for staff login brute-force protection,
temporary account lockout, failure counter reset, and user enumeration defense.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache
from django.contrib.auth import get_user_model
from dashboard.services import is_login_locked, reset_login_failures, record_login_failure

User = get_user_model()


class LoginBruteForceSecurityTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='auth_staff',
            password='CorrectPassword123!',
            is_staff=True,
            is_active=True,
        )

    def tearDown(self):
        cache.clear()

    def test_repeated_failed_logins_trigger_lockout(self):
        # Attempt 5 failed logins with wrong password
        for i in range(5):
            response = self.client.post(reverse('dashboard:login'), data={
                'username': 'auth_staff',
                'password': f'WrongPass{i}!',
            }, REMOTE_ADDR='198.51.100.10')
            self.assertEqual(response.status_code, 200)

        # 6th attempt should be blocked by lockout
        response = self.client.post(reverse('dashboard:login'), data={
            'username': 'auth_staff',
            'password': 'CorrectPassword123!',  # Even with correct password, blocked by lockout
        }, REMOTE_ADDR='198.51.100.10')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'temporarily locked')

    def test_lockout_does_not_reveal_user_existence(self):
        # Failed attempts on nonexistent username
        for i in range(5):
            self.client.post(reverse('dashboard:login'), data={
                'username': 'nonexistent_user',
                'password': 'SomePassword!',
            }, REMOTE_ADDR='198.51.100.20')

        # Both real and nonexistent user get identical lockout response
        resp_fake = self.client.post(reverse('dashboard:login'), data={
            'username': 'nonexistent_user',
            'password': 'SomePassword!',
        }, REMOTE_ADDR='198.51.100.20')

        resp_real = self.client.post(reverse('dashboard:login'), data={
            'username': 'auth_staff',
            'password': 'SomePassword!',
        }, REMOTE_ADDR='198.51.100.20')

        self.assertContains(resp_fake, 'temporarily locked')
        self.assertContains(resp_real, 'temporarily locked')

    def test_successful_login_resets_failure_counter(self):
        # Fail 3 times (less than threshold of 5)
        for i in range(3):
            self.client.post(reverse('dashboard:login'), data={
                'username': 'auth_staff',
                'password': f'WrongPass{i}!',
            }, REMOTE_ADDR='198.51.100.30')

        # Successful login resets the counter
        success_resp = self.client.post(reverse('dashboard:login'), data={
            'username': 'auth_staff',
            'password': 'CorrectPassword123!',
        }, REMOTE_ADDR='198.51.100.30')
        self.assertRedirects(success_resp, reverse('dashboard:overview'))

        # Now 3 more failed attempts should NOT trigger lockout (counter was reset)
        self.client.logout()
        for i in range(3):
            resp = self.client.post(reverse('dashboard:login'), data={
                'username': 'auth_staff',
                'password': f'WrongPass{i}!',
            }, REMOTE_ADDR='198.51.100.30')
            self.assertEqual(resp.status_code, 200)
            self.assertNotContains(resp, 'temporarily locked')

    def test_lockout_service_helpers_direct(self):
        ip = '203.0.113.50'
        username = 'test_helper_user'

        self.assertFalse(is_login_locked(ip, username))

        for _ in range(4):
            record_login_failure(ip, username)
        self.assertFalse(is_login_locked(ip, username))

        record_login_failure(ip, username)
        self.assertTrue(is_login_locked(ip, username))

        reset_login_failures(ip, username)
        self.assertFalse(is_login_locked(ip, username))
