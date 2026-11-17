"""
Unit & integration tests for centralized lead status transition validation,
state machine enforcement, audit trail creation, and form bypass prevention.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from inquiries.models import Inquiry, LeadStatus, ServiceChoices, LeadStatusHistory
from dashboard.services import execute_status_transition, is_valid_status_transition
from dashboard.forms import LeadForm

User = get_user_model()


class StatusTransitionValidationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='trans_staff',
            password='StaffPassword123!',
            is_staff=True,
            is_active=True
        )
        self.client.login(username='trans_staff', password='StaffPassword123!')

        self.lead = Inquiry.objects.create(
            reference_id='SS-20261117-TR01',
            full_name='Transition Test Customer',
            mobile_number='9876543210',
            email='trans@example.com',
            service=ServiceChoices.COMPANY_INCORPORATION,
            status=LeadStatus.NEW,
        )

    def test_state_machine_allowed_transitions(self):
        # NEW can transition to CONTACTED, FOLLOW_UP, PROPOSAL_SENT, MATURE, CLOSED
        self.assertTrue(is_valid_status_transition(LeadStatus.NEW, LeadStatus.CONTACTED))
        self.assertTrue(is_valid_status_transition(LeadStatus.NEW, LeadStatus.FOLLOW_UP))
        self.assertTrue(is_valid_status_transition(LeadStatus.NEW, LeadStatus.PROPOSAL_SENT))
        self.assertTrue(is_valid_status_transition(LeadStatus.NEW, LeadStatus.CLOSED))

        # Reopening: CLOSED can transition to CONTACTED or FOLLOW_UP
        self.assertTrue(is_valid_status_transition(LeadStatus.CLOSED, LeadStatus.CONTACTED))
        self.assertTrue(is_valid_status_transition(LeadStatus.CLOSED, LeadStatus.FOLLOW_UP))

    def test_state_machine_disallowed_transitions(self):
        # Transition to same status (no-op) must be rejected
        self.assertFalse(is_valid_status_transition(LeadStatus.NEW, LeadStatus.NEW))
        self.assertFalse(is_valid_status_transition(LeadStatus.CONTACTED, LeadStatus.CONTACTED))

        # Once an inquiry leaves NEW, it can NEVER return to NEW
        self.assertFalse(is_valid_status_transition(LeadStatus.CONTACTED, LeadStatus.NEW))
        self.assertFalse(is_valid_status_transition(LeadStatus.FOLLOW_UP, LeadStatus.NEW))
        self.assertFalse(is_valid_status_transition(LeadStatus.PROPOSAL_SENT, LeadStatus.NEW))
        self.assertFalse(is_valid_status_transition(LeadStatus.MATURE, LeadStatus.NEW))
        self.assertFalse(is_valid_status_transition(LeadStatus.CLOSED, LeadStatus.NEW))

        # CLOSED cannot jump directly to MATURE or PROPOSAL_SENT
        self.assertFalse(is_valid_status_transition(LeadStatus.CLOSED, LeadStatus.MATURE))
        self.assertFalse(is_valid_status_transition(LeadStatus.CLOSED, LeadStatus.PROPOSAL_SENT))

    def test_execute_status_transition_service_valid(self):
        success, msg, updated_lead = execute_status_transition(
            inquiry_id=self.lead.id,
            new_status=LeadStatus.CONTACTED,
            acting_user=self.staff_user,
            remarks='First phone discussion completed.'
        )
        self.assertTrue(success)
        self.assertIn('successfully updated', msg)
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.status, LeadStatus.CONTACTED)

        # Audit trail must be recorded
        history = LeadStatusHistory.objects.filter(inquiry=self.lead).first()
        self.assertIsNotNone(history)
        self.assertEqual(history.previous_status, LeadStatus.NEW)
        self.assertEqual(history.new_status, LeadStatus.CONTACTED)
        self.assertEqual(history.updated_by, self.staff_user)

    def test_execute_status_transition_service_rejects_invalid_transition(self):
        # Move lead to CONTACTED first
        self.lead.status = LeadStatus.CONTACTED
        self.lead.save()

        # Attempt illegal transition: CONTACTED -> NEW
        success, msg, _ = execute_status_transition(
            inquiry_id=self.lead.id,
            new_status=LeadStatus.NEW,
            acting_user=self.staff_user,
            remarks='Trying to return contacted lead to new.'
        )
        self.assertFalse(success)
        self.assertIn('Cannot transition lead', msg)
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.status, LeadStatus.CONTACTED)

    def test_lead_edit_form_enforces_central_status_transition(self):
        # Set lead to CONTACTED
        self.lead.status = LeadStatus.CONTACTED
        self.lead.save()

        # Submit edit form attempting illegal transition to NEW
        url = reverse('dashboard:lead_edit', args=[self.lead.reference_id])
        response = self.client.post(url, data={
            'full_name': 'Updated Name',
            'mobile_number': '9876543210',
            'email': 'trans@example.com',
            'service': ServiceChoices.COMPANY_INCORPORATION,
            'status': LeadStatus.NEW,  # Disallowed transition
        })

        # Form must reject invalid transition
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cannot transition lead')
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.status, LeadStatus.CONTACTED)

    def test_lead_edit_form_valid_status_change_creates_audit_history(self):
        # Submit valid edit transition from NEW to PROPOSAL_SENT
        url = reverse('dashboard:lead_edit', args=[self.lead.reference_id])
        response = self.client.post(url, data={
            'full_name': 'Transition Test Customer',
            'mobile_number': '9876543210',
            'email': 'trans@example.com',
            'service': ServiceChoices.COMPANY_INCORPORATION,
            'status': LeadStatus.PROPOSAL_SENT,
        })
        self.assertRedirects(response, reverse('dashboard:lead_detail', args=[self.lead.reference_id]))

        self.lead.refresh_from_db()
        self.assertEqual(self.lead.status, LeadStatus.PROPOSAL_SENT)

        # Audit trail entry must exist
        history = LeadStatusHistory.objects.filter(inquiry=self.lead, new_status=LeadStatus.PROPOSAL_SENT).first()
        self.assertIsNotNone(history)
        self.assertEqual(history.previous_status, LeadStatus.NEW)
        self.assertEqual(history.updated_by, self.staff_user)
