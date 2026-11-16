"""
Unit tests for Inquiry and LeadStatusHistory database models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from inquiries.models import Inquiry, LeadStatusHistory, ServiceChoices, LeadStatus

User = get_user_model()


class InquiryModelTests(TestCase):
    def setUp(self):
        self.inquiry = Inquiry.objects.create(
            reference_id='SS-20261116-A1B2',
            full_name='Vikram Malhotra',
            mobile_number='9876543210',
            email='vikram@example.com',
            service=ServiceChoices.COMPANY_INCORPORATION,
            message='Need guidance on incorporating a Private Limited entity.',
            status=LeadStatus.NEW,
        )

    def test_inquiry_string_representation(self):
        self.assertIn('SS-20261116-A1B2', str(self.inquiry))
        self.assertIn('Vikram Malhotra', str(self.inquiry))

    def test_default_status_is_new(self):
        new_inq = Inquiry.objects.create(
            reference_id='SS-20261116-C3D4',
            full_name='Anita Sharma',
            mobile_number='9123456780',
            email='anita@example.com',
            service=ServiceChoices.DPIIT_RECOGNITION,
        )
        self.assertEqual(new_inq.status, LeadStatus.NEW)

    def test_whatsapp_url_generation_for_valid_number(self):
        url = self.inquiry.get_whatsapp_url()
        self.assertIsNotNone(url)
        self.assertTrue(url.startswith('https://wa.me/919876543210?text='))
        self.assertIn('SS-20261116-A1B2', url)
        self.assertIn('Vikram', url)

    def test_whatsapp_url_returns_none_for_invalid_number(self):
        self.inquiry.mobile_number = '123'  # Not 10 digits
        self.assertIsNone(self.inquiry.get_whatsapp_url())

    def test_status_badge_classes(self):
        self.assertEqual(self.inquiry.status_badge_class, 'bg-primary text-white')
        self.inquiry.status = LeadStatus.MATURE
        self.assertEqual(self.inquiry.status_badge_class, 'bg-success text-white')
        self.inquiry.status = LeadStatus.CLOSED
        self.assertEqual(self.inquiry.status_badge_class, 'bg-dark text-white')

    def test_lead_status_history_cascade(self):
        staff = User.objects.create_user(username='staff_test', password='TestPassword123!', is_staff=True)
        history = LeadStatusHistory.objects.create(
            inquiry=self.inquiry,
            previous_status=LeadStatus.NEW,
            new_status=LeadStatus.CONTACTED,
            updated_by=staff,
            remarks='First outreach call completed.',
        )
        self.assertEqual(self.inquiry.status_history.count(), 1)
        self.assertEqual(history.updated_by, staff)

        # Deleting inquiry should cascade delete history
        inquiry_id = self.inquiry.id
        self.inquiry.delete()
        self.assertFalse(LeadStatusHistory.objects.filter(inquiry_id=inquiry_id).exists())

    def test_lead_status_history_user_set_null(self):
        staff = User.objects.create_user(username='staff_temp', password='TestPassword123!', is_staff=True)
        history = LeadStatusHistory.objects.create(
            inquiry=self.inquiry,
            previous_status=LeadStatus.NEW,
            new_status=LeadStatus.FOLLOW_UP,
            updated_by=staff,
            remarks='Test preservation on user delete.',
        )
        staff.delete()
        history.refresh_from_db()
        self.assertIsNone(history.updated_by)
