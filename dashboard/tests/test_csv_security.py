"""
Tests for CSV export formula injection protection (CSV Injection).
Verifies that dangerous trigger characters (=, +, -, @, tab, CR, pipe, %) are neutralized
while preserving readability for legitimate business data.
"""
import io
import csv
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from inquiries.models import Inquiry, ServiceChoices, LeadStatus
from dashboard.services import sanitize_csv_value

User = get_user_model()


class CSVInjectionSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='csv_admin',
            password='StaffPassword123!',
            is_staff=True,
            is_active=True
        )
        self.client.login(username='csv_admin', password='StaffPassword123!')

    def test_sanitize_csv_value_unit(self):
        # Malicious payloads starting with dangerous formula characters
        self.assertEqual(sanitize_csv_value('=SUM(1,2)'), "'=SUM(1,2)")
        self.assertEqual(sanitize_csv_value('+12345'), "'+12345")
        self.assertEqual(sanitize_csv_value('-100'), "'-100")
        self.assertEqual(sanitize_csv_value('@HYPERLINK("http://evil.com")'), "'@HYPERLINK(\"http://evil.com\")")
        self.assertEqual(sanitize_csv_value('\t=cmd'), "'\t=cmd")
        self.assertEqual(sanitize_csv_value('\r=cmd'), "'\r=cmd")
        self.assertEqual(sanitize_csv_value('|calc'), "'|calc")
        self.assertEqual(sanitize_csv_value('%0A'), "'%0A")

        # Payloads with leading whitespace followed by dangerous characters
        self.assertEqual(sanitize_csv_value('   =2+2'), "'   =2+2")
        self.assertEqual(sanitize_csv_value('  @SUM()'), "'  @SUM()")

        # Normal business values must NOT be prefixed with a single quote
        self.assertEqual(sanitize_csv_value('Aarav Mehta'), 'Aarav Mehta')
        self.assertEqual(sanitize_csv_value('9876543210'), '9876543210')
        self.assertEqual(sanitize_csv_value('aarav@example.com'), 'aarav@example.com')
        self.assertEqual(sanitize_csv_value('Company Incorporation'), 'Company Incorporation')
        self.assertEqual(sanitize_csv_value(''), '')
        self.assertEqual(sanitize_csv_value(None), '')

    def test_csv_export_endpoint_neutralizes_malicious_formulas(self):
        # Create lead with potential formula injection payloads
        Inquiry.objects.create(
            reference_id='SS-20261117-MAL1',
            full_name='=cmd|/C calc!A0',
            mobile_number='9876543210',
            email='malicious@example.com',
            service=ServiceChoices.TRADEMARK_REGISTRATION,
            status=LeadStatus.NEW,
            message='@SUM(1, 99) and -some dangerous text',
        )
        Inquiry.objects.create(
            reference_id='SS-20261117-NORM',
            full_name='Priya Nair',
            mobile_number='9123456780',
            email='priya@example.com',
            service=ServiceChoices.COMPANY_INCORPORATION,
            status=LeadStatus.CONTACTED,
            message='Legitimate customer message.',
        )

        response = self.client.get(reverse('dashboard:export_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="sahay_leads_', response['Content-Disposition'])

        csv_content = response.content.decode('utf-8')
        reader = csv.reader(io.StringIO(csv_content))
        rows = list(reader)

        # Header verification
        headers = rows[0]
        self.assertEqual(headers[0], 'Reference ID')
        self.assertEqual(headers[1], 'Customer Name')

        # Find rows by reference ID
        mal_row = [r for r in rows if r[0] == 'SS-20261117-MAL1'][0]
        norm_row = [r for r in rows if r[0] == 'SS-20261117-NORM'][0]

        # Malicious customer name must be neutralized with leading quote
        self.assertTrue(mal_row[1].startswith("'="))
        self.assertIn("'=cmd|/C calc!A0", mal_row[1])

        # Malicious message starting with @ must be neutralized
        self.assertTrue(mal_row[9].startswith("'@"))

        # Normal row must preserve clean text without quotes prepended
        self.assertEqual(norm_row[1], 'Priya Nair')
        self.assertEqual(norm_row[2], '9123456780')
        self.assertEqual(norm_row[3], 'priya@example.com')
        self.assertEqual(norm_row[9], 'Legitimate customer message.')
