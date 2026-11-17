"""
Unit tests for follow-up date calculation, timezone boundaries,
and mutual exclusivity between Overdue, Due Today, and Upcoming queues.
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from django.test import TestCase
from django.utils import timezone
from inquiries.models import Inquiry, LeadStatus, ServiceChoices
from dashboard.services import get_follow_ups_data


class FollowUpLogicAndCountTests(TestCase):
    def setUp(self):
        # Configure Indian Standard Time
        self.tz = timezone.get_current_timezone()
        now_local = timezone.now().astimezone(self.tz)
        self.today_date = now_local.date()

        self.start_of_today = datetime.combine(self.today_date, datetime.min.time(), tzinfo=self.tz)
        self.start_of_tomorrow = self.start_of_today + timedelta(days=1)

    def test_timezone_is_asia_kolkata(self):
        # Verify configured application timezone
        self.assertEqual(str(self.tz), 'Asia/Kolkata')

    def test_overdue_today_upcoming_are_mutually_exclusive(self):
        # 1. Lead overdue (scheduled yesterday)
        overdue_lead = Inquiry.objects.create(
            reference_id='SS-20261117-OVR1',
            full_name='Overdue Customer',
            mobile_number='9876543210',
            email='overdue@example.com',
            service=ServiceChoices.COMPANY_INCORPORATION,
            status=LeadStatus.CONTACTED,
            follow_up_date=self.start_of_today - timedelta(hours=5),
        )

        # 2. Lead due today (scheduled for this afternoon)
        today_lead = Inquiry.objects.create(
            reference_id='SS-20261117-TOD1',
            full_name='Today Customer',
            mobile_number='9876543211',
            email='today@example.com',
            service=ServiceChoices.TRADEMARK_REGISTRATION,
            status=LeadStatus.FOLLOW_UP,
            follow_up_date=self.start_of_today + timedelta(hours=14),
        )

        # 3. Lead upcoming (scheduled for tomorrow)
        upcoming_lead = Inquiry.objects.create(
            reference_id='SS-20261117-UPC1',
            full_name='Upcoming Customer',
            mobile_number='9876543212',
            email='upcoming@example.com',
            service=ServiceChoices.SEED_FUND_SUPPORT,
            status=LeadStatus.PROPOSAL_SENT,
            follow_up_date=self.start_of_tomorrow + timedelta(hours=3),
        )

        # 4. Lead unscheduled
        unscheduled_lead = Inquiry.objects.create(
            reference_id='SS-20261117-UNS1',
            full_name='Unscheduled Customer',
            mobile_number='9876543213',
            email='unscheduled@example.com',
            service=ServiceChoices.DPIIT_RECOGNITION,
            status=LeadStatus.NEW,
            follow_up_date=None,
        )

        data = get_follow_ups_data()
        overdue_list = list(data['overdue'])
        today_list = list(data['due_today'])
        upcoming_list = list(data['upcoming'])
        unscheduled_list = list(data['unscheduled'])

        # Check memberships
        self.assertIn(overdue_lead, overdue_list)
        self.assertNotIn(overdue_lead, today_list)
        self.assertNotIn(overdue_lead, upcoming_list)

        self.assertIn(today_lead, today_list)
        self.assertNotIn(today_lead, overdue_list)
        self.assertNotIn(today_lead, upcoming_list)

        self.assertIn(upcoming_lead, upcoming_list)
        self.assertNotIn(upcoming_lead, overdue_list)
        self.assertNotIn(upcoming_lead, today_list)

        self.assertIn(unscheduled_lead, unscheduled_list)

        # Mutually exclusive counts
        self.assertEqual(len(overdue_list), 1)
        self.assertEqual(len(today_list), 1)
        self.assertEqual(len(upcoming_list), 1)

        # total_due represents unique count of overdue + due today
        self.assertEqual(data['total_due'], 2)

    def test_midnight_boundary_conditions(self):
        # Exactly 1 second before midnight today (23:59:59 yesterday) -> Overdue
        lead_yesterday_boundary = Inquiry.objects.create(
            reference_id='SS-20261117-BND1',
            full_name='Yesterday Boundary',
            mobile_number='9876543220',
            email='bnd1@example.com',
            service=ServiceChoices.COMPANY_INCORPORATION,
            status=LeadStatus.NEW,
            follow_up_date=self.start_of_today - timedelta(seconds=1),
        )

        # Exactly 00:00:00 today IST -> Due Today
        lead_today_start = Inquiry.objects.create(
            reference_id='SS-20261117-BND2',
            full_name='Today Midnight Start',
            mobile_number='9876543221',
            email='bnd2@example.com',
            service=ServiceChoices.COMPANY_INCORPORATION,
            status=LeadStatus.NEW,
            follow_up_date=self.start_of_today,
        )

        # Exactly 23:59:59 today IST -> Due Today
        lead_today_end = Inquiry.objects.create(
            reference_id='SS-20261117-BND3',
            full_name='Today Midnight End',
            mobile_number='9876543222',
            email='bnd3@example.com',
            service=ServiceChoices.COMPANY_INCORPORATION,
            status=LeadStatus.NEW,
            follow_up_date=self.start_of_tomorrow - timedelta(seconds=1),
        )

        # Exactly 00:00:00 tomorrow IST -> Upcoming
        lead_tomorrow_start = Inquiry.objects.create(
            reference_id='SS-20261117-BND4',
            full_name='Tomorrow Midnight Start',
            mobile_number='9876543223',
            email='bnd4@example.com',
            service=ServiceChoices.COMPANY_INCORPORATION,
            status=LeadStatus.NEW,
            follow_up_date=self.start_of_tomorrow,
        )

        data = get_follow_ups_data()
        self.assertIn(lead_yesterday_boundary, list(data['overdue']))
        self.assertNotIn(lead_yesterday_boundary, list(data['due_today']))

        self.assertIn(lead_today_start, list(data['due_today']))
        self.assertNotIn(lead_today_start, list(data['overdue']))

        self.assertIn(lead_today_end, list(data['due_today']))
        self.assertNotIn(lead_today_end, list(data['overdue']))

        self.assertIn(lead_tomorrow_start, list(data['upcoming']))
        self.assertNotIn(lead_tomorrow_start, list(data['due_today']))
        self.assertNotIn(lead_tomorrow_start, list(data['overdue']))

    def test_mature_and_closed_leads_excluded_from_follow_ups(self):
        # Mature or Closed leads should not appear in active follow-up queues
        Inquiry.objects.create(
            reference_id='SS-20261117-EXC1',
            full_name='Mature Customer',
            mobile_number='9876543230',
            email='mature@example.com',
            service=ServiceChoices.COMPANY_INCORPORATION,
            status=LeadStatus.MATURE,
            follow_up_date=self.start_of_today - timedelta(days=2),
        )
        Inquiry.objects.create(
            reference_id='SS-20261117-EXC2',
            full_name='Closed Customer',
            mobile_number='9876543231',
            email='closed@example.com',
            service=ServiceChoices.COMPANY_INCORPORATION,
            status=LeadStatus.CLOSED,
            follow_up_date=self.start_of_today + timedelta(hours=2),
        )

        data = get_follow_ups_data()
        self.assertEqual(data['overdue'].count(), 0)
        self.assertEqual(data['due_today'].count(), 0)
        self.assertEqual(data['total_due'], 0)
