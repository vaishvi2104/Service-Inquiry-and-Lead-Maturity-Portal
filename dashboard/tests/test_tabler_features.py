"""
Unit & integration tests for new Tabler dashboard features:
Kanban pipeline, follow-ups desk, lead creation/editing, CSV export,
status history audit log, and staff profile settings.
"""
from datetime import timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from inquiries.models import Inquiry, LeadStatus, ServiceChoices, LeadStatusHistory

User = get_user_model()


class TablerFeaturesTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='tabler_admin',
            password='StaffPassword123!',
            is_staff=True,
            is_active=True,
            first_name='Admin',
            last_name='User',
            email='admin@startupsahay.com',
        )
        self.client.login(username='tabler_admin', password='StaffPassword123!')

        self.lead = Inquiry.objects.create(
            reference_id='SS-20261116-TAB1',
            full_name='Aarav Mehta',
            mobile_number='9876543210',
            email='aarav@example.com',
            service=ServiceChoices.COMPANY_INCORPORATION,
            status=LeadStatus.NEW,
            follow_up_date=timezone.now() - timedelta(days=1),  # overdue (earlier than today)
        )

    def test_kanban_view_renders_all_six_columns(self):
        response = self.client.get(reverse('dashboard:kanban'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lead Maturity Kanban Board')
        columns = response.context['columns']
        self.assertEqual(len(columns), 6)
        # Check that lead is in New Inquiry column
        new_col = [c for c in columns if c['key'] == LeadStatus.NEW][0]
        self.assertEqual(new_col['count'], 1)

    def test_kanban_move_updates_stage_and_creates_history(self):
        url = reverse('dashboard:kanban_move', args=[self.lead.reference_id])
        response = self.client.post(url, data={
            'target_stage': LeadStatus.PROPOSAL_SENT,
            'remarks': 'Moved directly via Kanban card menu.',
        })
        self.assertRedirects(response, reverse('dashboard:kanban'))

        self.lead.refresh_from_db()
        self.assertEqual(self.lead.status, LeadStatus.PROPOSAL_SENT)

        history = LeadStatusHistory.objects.filter(inquiry=self.lead, new_status=LeadStatus.PROPOSAL_SENT).first()
        self.assertIsNotNone(history)
        self.assertEqual(history.updated_by, self.staff_user)
        self.assertIn('Kanban', history.remarks)

    def test_follow_ups_view_renders_categories(self):
        response = self.client.get(reverse('dashboard:follow_ups'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Follow-up Management Desk')
        follow_ups = response.context['follow_ups']
        self.assertTrue(self.lead in follow_ups['overdue'])

    def test_schedule_follow_up_action(self):
        url = reverse('dashboard:schedule_follow_up', args=[self.lead.reference_id])
        future_date = (timezone.now() + timedelta(days=3)).strftime('%Y-%m-%dT14:30')
        response = self.client.post(url, data={
            'follow_up_date': future_date,
            'remarks': 'Follow-up to review incorporation documents.',
        })
        self.assertRedirects(response, reverse('dashboard:lead_detail', args=[self.lead.reference_id]))

        self.lead.refresh_from_db()
        self.assertIsNotNone(self.lead.follow_up_date)
        self.assertIn('review incorporation documents', self.lead.internal_notes)

    def test_lead_create_view_creates_inquiry_and_history(self):
        url = reverse('dashboard:lead_create')
        response = self.client.post(url, data={
            'full_name': 'Kavita Patel',
            'mobile_number': '9123456780',
            'email': 'kavita@example.com',
            'service': ServiceChoices.DPIIT_RECOGNITION,
            'status': LeadStatus.CONTACTED,
            'message': 'Walk-in inquiry for DPIIT recognition.',
        })
        new_inquiry = Inquiry.objects.filter(email='kavita@example.com').first()
        self.assertIsNotNone(new_inquiry)
        self.assertRedirects(response, reverse('dashboard:lead_detail', args=[new_inquiry.reference_id]))
        self.assertEqual(new_inquiry.status, LeadStatus.CONTACTED)
        self.assertEqual(new_inquiry.status_history.count(), 1)

    def test_lead_edit_view_updates_fields(self):
        url = reverse('dashboard:lead_edit', args=[self.lead.reference_id])
        response = self.client.post(url, data={
            'full_name': 'Aarav Mehta Updated',
            'mobile_number': '9876543210',
            'email': 'aarav.updated@example.com',
            'service': ServiceChoices.TRADEMARK_REGISTRATION,
            'status': LeadStatus.FOLLOW_UP,
            'message': 'Updated inquiry description.',
        })
        self.assertRedirects(response, reverse('dashboard:lead_detail', args=[self.lead.reference_id]))
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.full_name, 'Aarav Mehta Updated')
        self.assertEqual(self.lead.service, ServiceChoices.TRADEMARK_REGISTRATION)
        self.assertEqual(self.lead.status, LeadStatus.FOLLOW_UP)

    def test_status_history_view_renders_and_filters(self):
        response = self.client.get(reverse('dashboard:status_history'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lead Status History')

        # Filter by reference ID
        filtered_resp = self.client.get(reverse('dashboard:status_history'), {'ref': 'SS-20261116-TAB1'})
        self.assertEqual(filtered_resp.status_code, 200)

    def test_advanced_search_view_filters_and_renders(self):
        response = self.client.get(reverse('dashboard:advanced_search'), {'q': 'Aarav'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Aarav Mehta')

    def test_csv_export_returns_csv_file(self):
        response = self.client.get(reverse('dashboard:export_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="sahay_leads_', response['Content-Disposition'])
        content = response.content.decode('utf-8')
        self.assertIn('Reference ID,Customer Name', content)
        self.assertIn('SS-20261116-TAB1', content)

    def test_profile_view_renders_user_data(self):
        response = self.client.get(reverse('dashboard:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'tabler_admin')
        self.assertContains(response, 'admin@startupsahay.com')

    def test_profile_update_changes_name(self):
        url = reverse('dashboard:profile')
        response = self.client.post(url, data={
            'action': 'update_profile',
            'first_name': 'Chief',
            'last_name': 'Advisor',
            'email': 'chief@startupsahay.com',
        })
        self.assertRedirects(response, reverse('dashboard:profile'))
        self.staff_user.refresh_from_db()
        self.assertEqual(self.staff_user.first_name, 'Chief')
        self.assertEqual(self.staff_user.last_name, 'Advisor')

    def test_all_tabler_pages_require_staff_auth(self):
        anonymous_client = Client()
        endpoints = [
            reverse('dashboard:overview'),
            reverse('dashboard:leads'),
            reverse('dashboard:kanban'),
            reverse('dashboard:follow_ups'),
            reverse('dashboard:lead_create'),
            reverse('dashboard:status_history'),
            reverse('dashboard:advanced_search'),
            reverse('dashboard:profile'),
            reverse('dashboard:export_csv'),
        ]
        for url in endpoints:
            resp = anonymous_client.get(url)
            self.assertEqual(resp.status_code, 302, f"Endpoint {url} did not redirect anonymous user")
            self.assertIn(reverse('dashboard:login'), resp.url)
