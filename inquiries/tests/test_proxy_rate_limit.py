"""
Tests for reverse-proxy-safe client IP extraction, spoofing protection,
and rate limiter fail-open resilience.
"""
from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory
from django.conf import settings
from inquiries.services import get_client_ip, is_valid_ip, check_rate_limit


class ProxyRateLimitTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_ip_validation_helper(self):
        self.assertTrue(is_valid_ip('192.168.1.1'))
        self.assertTrue(is_valid_ip('203.0.113.195'))
        self.assertTrue(is_valid_ip('2001:db8::1'))
        self.assertFalse(is_valid_ip('not-an-ip'))
        self.assertFalse(is_valid_ip('<script>alert(1)</script>'))
        self.assertFalse(is_valid_ip(''))
        self.assertFalse(is_valid_ip(None))

    def test_remote_addr_used_when_proxy_disabled(self):
        request = self.factory.get('/', REMOTE_ADDR='203.0.113.5', HTTP_X_FORWARDED_FOR='198.51.100.99')
        with patch.object(settings, 'USE_X_FORWARDED_FOR', False):
            ip = get_client_ip(request)
            self.assertEqual(ip, '203.0.113.5')

    def test_forwarded_ip_extracted_when_proxy_enabled(self):
        request = self.factory.get('/', REMOTE_ADDR='10.0.0.1', HTTP_X_FORWARDED_FOR='203.0.113.10, 10.0.0.1')
        with patch.object(settings, 'USE_X_FORWARDED_FOR', True):
            ip = get_client_ip(request)
            self.assertEqual(ip, '203.0.113.10')

    def test_spoofed_or_invalid_forwarded_ip_falls_back_safely(self):
        request = self.factory.get('/', REMOTE_ADDR='203.0.113.5', HTTP_X_FORWARDED_FOR='malicious-header-string, <svg>')
        with patch.object(settings, 'USE_X_FORWARDED_FOR', True):
            ip = get_client_ip(request)
            # Must safely ignore the invalid header and fall back to REMOTE_ADDR
            self.assertEqual(ip, '203.0.113.5')

    def test_missing_or_invalid_remote_addr_falls_back_to_localhost(self):
        request = self.factory.get('/', REMOTE_ADDR='invalid_ip_text')
        with patch.object(settings, 'USE_X_FORWARDED_FOR', False):
            ip = get_client_ip(request)
            self.assertEqual(ip, '127.0.0.1')

    def test_rate_limiter_fails_open_when_cache_raises_exception(self):
        request = self.factory.get('/', REMOTE_ADDR='203.0.113.50')
        # Simulate Redis/cache network timeout or connection failure
        with patch('inquiries.services.cache.get', side_effect=Exception("Redis Connection Refused")):
            # Must NOT raise 500 error; must fail open safely returning False (allowed)
            throttled = check_rate_limit(request)
            self.assertFalse(throttled)
