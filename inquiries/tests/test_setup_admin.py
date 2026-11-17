"""
Unit tests for the setup_admin management command.
Verifies idempotency, password preservation, and elimination of hardcoded defaults.
"""
import os
from unittest.mock import patch
from io import StringIO
from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth import get_user_model

User = get_user_model()


class SetupAdminCommandTests(TestCase):
    def test_setup_admin_creates_new_superuser_with_env_password(self):
        out = StringIO()
        env = {
            'ADMIN_USERNAME': 'env_admin',
            'ADMIN_EMAIL': 'env_admin@startupsahay.com',
            'ADMIN_PASSWORD': 'SecureEnvPassword123!',
        }
        with patch.dict(os.environ, env):
            call_command('setup_admin', stdout=out)

        user = User.objects.filter(username='env_admin').first()
        self.assertIsNotNone(user)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.check_password('SecureEnvPassword123!'))
        self.assertIn("created successfully", out.getvalue())

    def test_setup_admin_does_not_reset_password_on_subsequent_runs(self):
        # 1. Initial creation
        out1 = StringIO()
        env = {
            'ADMIN_USERNAME': 'deploy_admin',
            'ADMIN_EMAIL': 'deploy_admin@startupsahay.com',
            'ADMIN_PASSWORD': 'OriginalPassword123!',
        }
        with patch.dict(os.environ, env):
            call_command('setup_admin', stdout=out1)

        user = User.objects.get(username='deploy_admin')
        self.assertTrue(user.check_password('OriginalPassword123!'))

        # 2. User changes their password in production
        user.set_password('UserChangedPassword456!')
        user.save()

        # 3. Subsequent deployment runs build.sh / setup_admin with different or default env
        out2 = StringIO()
        env_redeploy = {
            'ADMIN_USERNAME': 'deploy_admin',
            'ADMIN_EMAIL': 'deploy_admin@startupsahay.com',
            'ADMIN_PASSWORD': 'DifferentPassword789!',
        }
        with patch.dict(os.environ, env_redeploy):
            call_command('setup_admin', stdout=out2)

        user.refresh_from_db()
        # CRITICAL ASSERTION: The user's changed password MUST be preserved!
        self.assertTrue(user.check_password('UserChangedPassword456!'))
        self.assertFalse(user.check_password('DifferentPassword789!'))
        self.assertIn("Password preserved", out2.getvalue())

    def test_setup_admin_without_password_warns_and_does_not_set_hardcoded_secret(self):
        out = StringIO()
        env = {
            'ADMIN_USERNAME': 'no_pass_admin',
            'ADMIN_EMAIL': 'nopass@startupsahay.com',
        }
        with patch.dict(os.environ, env, clear=True):
            call_command('setup_admin', stdout=out)

        # Must not create user with hardcoded password
        self.assertFalse(User.objects.filter(username='no_pass_admin').exists())
        self.assertIn("ADMIN_PASSWORD environment variable not set", out.getvalue())
