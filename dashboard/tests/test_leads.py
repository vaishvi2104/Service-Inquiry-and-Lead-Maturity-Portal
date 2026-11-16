"""
Tests for lead management, dynamic aggregation, search, filtering, and status workflows.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from inquiries.models import Inquiry, LeadStatus, ServiceChoices, LeadStatusHistory

User = get_user_model()


class DashboardLeadsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='lead_manager',
            password='StaffPassword123!',
            is_staff=True,
            is_active=True
        )
        self.client.login(username='lead_manager', password='StaffPassword123!')

        # Create sample leads across stages
        self.lead1 = Inquiry.objects.create(
            reference_id='SS-20261116-0001',
            full_name='Aarav Patel',
            mobile_number='9825012345',
            email='aarav@example.com',
            service=ServiceChoices.COMPANY_INCORPORATION,
            status=LeadStatus.NEW,
        )
        self.lead2 = Inquiry.objects.create(
            reference_id='SS-20261116-0002',
            full_name='Bhavna Desai',
            mobile_number='9879012345',
            email='bhavna@example.com',
            service=ServiceChoices.TRADEMARK_REGISTRATION,
            status=LeadStatus.CONTACTED,
        )
        self.lead3 = Inquiry.objects.create(
            reference_id='SS-20261116-0003',
            full_name='Chetan Joshi',
            mobile_number='9998012345',
            email='chetan@example.com',
            service=ServiceChoices.SEED_FUND_SUPPORT,
            status=LeadStatus.MATURE,
        )

    def test_overview_metrics_aggregation(self):
        response = self.client.get(reverse('dashboard:overview'))
        self.assertEqual(response.status_code, 200)
        metrics = response.context['metrics']
        self.assertEqual(metrics['total'], 3)
        self.assertEqual(metrics['new'], 1)
        self.assertEqual(metrics['contacted'], 1)
        self.assertEqual(metrics['mature'], 1)
        self.assertEqual(metrics['follow_up'], 0)

    def test_leads_ordered_newest_first(self):
        response = self.client.get(reverse('dashboard:leads'))
        self.assertEqual(response.status_code, 200)
        leads = list(response.context['leads'])
        # Newest (lead3) should appear first
        self.assertEqual(leads[0].reference_id, self.lead3.reference_id)
        self.assertEqual(leads[-1].reference_id, self.lead1.reference_id)

    def test_search_by_name(self):
        response = self.client.get(reverse('dashboard:leads'), {'q': 'Aarav'})
        self.assertEqual(response.status_code, 200)
        leads = list(response.context['leads'])
        self.assertEqual(len(leads), 1)
        self.assertEqual(leads[0].reference_id, self.lead1.reference_id)

    def test_search_by_phone(self):
        response = self.client.get(reverse('dashboard:leads'), {'q': '9879012345'})
        self.assertEqual(response.status_code, 200)
        leads = list(response.context['leads'])
        self.assertEqual(len(leads), 1)
        self.assertEqual(leads[0].reference_id, self.lead2.reference_id)

    def test_search_by_reference_id(self):
        response = self.client.get(reverse('dashboard:leads'), {'q': 'SS-20261116-0003'})
        self.assertEqual(response.status_code, 200)
        leads = list(response.context['leads'])
        self.assertEqual(len(leads), 1)
        self.assertEqual(leads[0].reference_id, self.lead3.reference_id)

    def test_filter_by_status(self):
        response = self.client.get(reverse('dashboard:leads'), {'status': LeadStatus.MATURE})
        self.assertEqual(response.status_code, 200)
        leads = list(response.context['leads'])
        self.assertEqual(len(leads), 1)
        self.assertEqual(leads[0].reference_id, self.lead3.reference_id)

    def test_search_and_status_combined(self):
        # Searching for 'Joshi' with status 'mature' matches lead3
        response = self.client.get(reverse('dashboard:leads'), {'q': 'Joshi', 'status': LeadStatus.MATURE})
        self.assertEqual(response.status_code, 200)
        leads = list(response.context['leads'])
        self.assertEqual(len(leads), 1)

        # Searching for 'Joshi' with status 'new' matches nothing
        empty_resp = self.client.get(reverse('dashboard:leads'), {'q': 'Joshi', 'status': LeadStatus.NEW})
        self.assertEqual(empty_resp.status_code, 200)
        self.assertEqual(len(list(empty_resp.context['leads'])), 0)

    def test_valid_status_transition_succeeds_and_creates_history(self):
        update_url = reverse('dashboard:lead_status_update', args=[self.lead1.reference_id])
        response = self.client.post(update_url, data={
            'new_status': LeadStatus.CONTACTED,
            'remarks': 'First consultation call placed. Client interested in OPC.',
        })
        self.assertRedirects(response, reverse('dashboard:lead_detail', args=[self.lead1.reference_id]))

        self.lead1.refresh_from_db()
        self.assertEqual(self.lead1.status, LeadStatus.CONTACTED)

        # Verify history entry
        history = LeadStatusHistory.objects.filter(inquiry=self.lead1).first()
        self.assertIsNotNone(history)
        self.assertEqual(history.previous_status, LeadStatus.NEW)
        self.assertEqual(history.new_status, LeadStatus.CONTACTED)
        self.assertEqual(history.updated_by, self.staff_user)
        self.assertIn('First consultation call', history.remarks)

    def test_no_op_same_status_update_rejected(self):
        initial_history_count = LeadStatusHistory.objects.filter(inquiry=self.lead1).count()
        update_url = reverse('dashboard:lead_status_update', args=[self.lead1.reference_id])
        # Attempt updating to the same status (NEW -> NEW)
        response = self.client.post(update_url, data={
            'new_status': LeadStatus.NEW,
            'remarks': 'Trying to re-save current status.',
        })
        self.assertRedirects(response, reverse('dashboard:lead_detail', args=[self.lead1.reference_id]))
        # History count must not increase for a no-op transition
        self.assertEqual(LeadStatusHistory.objects.filter(inquiry=self.lead1).count(), initial_history_count)

    def test_invalid_status_value_rejected(self):
        update_url = reverse('dashboard:lead_status_update', args=[self.lead1.reference_id])
        response = self.client.post(update_url, data={
            'new_status': 'invalid_nonexistent_status',
            'remarks': 'Trying to set an illegal status.',
        })
        self.assertEqual(response.status_code, 302)
        self.lead1.refresh_from_db()
        self.assertEqual(self.lead1.status, LeadStatus.NEW)
