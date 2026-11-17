"""
Unit & integration tests for follow-up notes data loss prevention,
character limit validation, historical note preservation, and FollowUpNote model records.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from inquiries.models import Inquiry, LeadStatus, ServiceChoices, FollowUpNote

User = get_user_model()


class FollowUpNotesDataLossTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='note_staff',
            password='StaffPassword123!',
            is_staff=True,
            is_active=True,
        )
        self.client.login(username='note_staff', password='StaffPassword123!')

        self.inquiry = Inquiry.objects.create(
            reference_id='SS-20261117-NOTE',
            full_name='Notes Test Customer',
            mobile_number='9876543210',
            email='notes@example.com',
            service=ServiceChoices.COMPANY_INCORPORATION,
            status=LeadStatus.CONTACTED,
            internal_notes='Initial consultation: Client interested in Pvt Ltd structure.',
        )

    def test_schedule_follow_up_creates_follow_up_note_record(self):
        url = reverse('dashboard:schedule_follow_up', args=[self.inquiry.reference_id])
        response = self.client.post(url, data={
            'follow_up_date': '2026-11-20T10:00',
            'remarks': 'Follow-up call to review MoA/AoA drafts.',
        })
        self.assertRedirects(response, reverse('dashboard:lead_detail', args=[self.inquiry.reference_id]))

        self.inquiry.refresh_from_db()
        self.assertIn('review MoA/AoA drafts', self.inquiry.internal_notes)
        self.assertIn('Initial consultation', self.inquiry.internal_notes)

        # Verify separate FollowUpNote model record created
        note_record = FollowUpNote.objects.filter(inquiry=self.inquiry).first()
        self.assertIsNotNone(note_record)
        self.assertEqual(note_record.content, 'Follow-up call to review MoA/AoA drafts.')
        self.assertEqual(note_record.created_by, self.staff_user)
        self.assertIsNotNone(note_record.created_at)

    def test_notes_exceeding_character_limit_do_not_silently_truncate(self):
        # Fill internal notes close to 2,000 characters (e.g. 1950 characters)
        original_history = 'Historical Note Chunk: ' + ('X' * 1900)
        self.inquiry.internal_notes = original_history
        self.inquiry.save(update_fields=['internal_notes'])

        url = reverse('dashboard:schedule_follow_up', args=[self.inquiry.reference_id])
        # Attempt to add a 200-character remark that would exceed the 2000-char boundary
        remarks = 'This is a long follow-up note that pushes total notes over the 2000 character limit.'
        response = self.client.post(url, data={
            'follow_up_date': '2026-11-20T10:00',
            'remarks': remarks,
        }, follow=True)

        # Must display clear error message to the user
        self.assertContains(response, 'limit of 2,000 characters exceeded')

        # CRITICAL ASSERTION: Previous notes MUST NOT be silently truncated!
        self.inquiry.refresh_from_db()
        self.assertEqual(self.inquiry.internal_notes, original_history)
        self.assertTrue(self.inquiry.internal_notes.startswith('Historical Note Chunk: '))

    def test_lead_form_rejects_internal_notes_over_2000_chars(self):
        url = reverse('dashboard:lead_edit', args=[self.inquiry.reference_id])
        response = self.client.post(url, data={
            'full_name': 'Notes Test Customer',
            'mobile_number': '9876543210',
            'email': 'notes@example.com',
            'service': ServiceChoices.COMPANY_INCORPORATION,
            'status': LeadStatus.CONTACTED,
            'internal_notes': 'A' * 2001,  # Exceeds max 2000
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '2000 characters')
