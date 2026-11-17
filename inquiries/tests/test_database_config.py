"""
Unit tests for environment-based database configuration parsing.
Verifies parsing of DATABASE_URL for PostgreSQL, SQLite, and safe local fallbacks.
"""
from pathlib import Path
from django.test import TestCase
from config.settings import _configure_database, BASE_DIR


class DatabaseConfigTests(TestCase):
    def test_default_sqlite_configuration(self):
        config = _configure_database()
        self.assertIn('ENGINE', config)
        self.assertIn('NAME', config)
        # In testing/development without DATABASE_URL, defaults to SQLite
        self.assertEqual(config['ENGINE'], 'django.db.backends.sqlite3')

    def test_parse_postgres_database_url(self):
        import os
        from unittest.mock import patch

        test_url = "postgresql://sahay_user:SecretPass123%40!@db.example.com:5433/startupsahay_prod"
        with patch.dict(os.environ, {'DATABASE_URL': test_url}):
            config = _configure_database()
            self.assertEqual(config['ENGINE'], 'django.db.backends.postgresql')
            self.assertEqual(config['NAME'], 'startupsahay_prod')
            self.assertEqual(config['USER'], 'sahay_user')
            self.assertEqual(config['PASSWORD'], 'SecretPass123@!')
            self.assertEqual(config['HOST'], 'db.example.com')
            self.assertEqual(config['PORT'], '5433')

    def test_parse_sqlite_database_url(self):
        import os
        from unittest.mock import patch

        test_url = "sqlite:///custom_db.sqlite3"
        with patch.dict(os.environ, {'DATABASE_URL': test_url}):
            config = _configure_database()
            self.assertEqual(config['ENGINE'], 'django.db.backends.sqlite3')
            self.assertTrue(str(config['NAME']).endswith('custom_db.sqlite3'))
