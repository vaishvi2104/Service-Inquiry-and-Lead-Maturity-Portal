"""
Database models for Start-Up Sahay Service Inquiry & Lead Management.
Uses strict relational constraints, explicit choices, indexes, and audit trails.
"""
import urllib.parse
from django.db import models
from django.contrib.auth import get_user_model
from inquiries.validators import validate_mobile_number, validate_full_name

User = get_user_model()


class ServiceChoices(models.TextChoices):
    COMPANY_INCORPORATION = 'company_incorporation', 'Company Incorporation'
    DPIIT_RECOGNITION = 'dpiit_recognition', 'Startup India DPIIT Recognition'
    TRADEMARK_REGISTRATION = 'trademark_registration', 'Trademark Registration'
    SEED_FUND_SUPPORT = 'seed_fund_support', 'Seed Fund Support'


class LeadStatus(models.TextChoices):
    NEW = 'new', 'New Inquiry'
    CONTACTED = 'contacted', 'Contacted'
    FOLLOW_UP = 'follow_up', 'Follow-up'
    PROPOSAL_SENT = 'proposal_sent', 'Proposal Sent'
    MATURE = 'mature', 'Mature'
    CLOSED = 'closed', 'Closed'


class Inquiry(models.Model):
    """
    Primary inquiry entity representing a prospective client inquiry
    submitted through the public customer portal.
    """
    id = models.BigAutoField(primary_key=True)
    reference_id = models.CharField(
        max_length=24,
        unique=True,
        db_index=True,
        editable=False,
        help_text='Non-guessable public reference identifier (e.g. SS-20261116-A8F2).'
    )
    full_name = models.CharField(
        max_length=120,
        validators=[validate_full_name],
        help_text='Customer full legal/business contact name.'
    )
    mobile_number = models.CharField(
        max_length=10,
        db_index=True,
        validators=[validate_mobile_number],
        help_text='10-digit Indian mobile number.'
    )
    email = models.EmailField(
        max_length=254,
        db_index=True,
        help_text='Valid primary email address.'
    )
    service = models.CharField(
        max_length=40,
        choices=ServiceChoices.choices,
        db_index=True,
        help_text='Selected consultancy service track.'
    )
    message = models.TextField(
        max_length=2000,
        blank=True,
        default='',
        help_text='Optional customer inquiry details (max 2000 characters).'
    )
    status = models.CharField(
        max_length=30,
        choices=LeadStatus.choices,
        default=LeadStatus.NEW,
        db_index=True,
        help_text='Current maturity stage of this inquiry.'
    )
    follow_up_date = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text='Scheduled follow-up date and time for customer contact.'
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_inquiries',
        help_text='Staff member assigned to manage this lead.'
    )
    internal_notes = models.TextField(
        max_length=2000,
        blank=True,
        default='',
        help_text='Internal staff notes and requirement details.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='Timestamp when the inquiry was submitted.'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Timestamp of latest inquiry modification.'
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at'], name='inquiry_status_created_idx'),
            models.Index(fields=['mobile_number', 'status'], name='inquiry_mobile_status_idx'),
            models.Index(fields=['reference_id'], name='inquiry_ref_id_idx'),
        ]
        verbose_name = 'Customer Inquiry'
        verbose_name_plural = 'Customer Inquiries'

    def __str__(self) -> str:
        return f"{self.reference_id} — {self.full_name} ({self.get_service_display()})"

    @property
    def service_label(self) -> str:
        return self.get_service_display()

    @property
    def status_label(self) -> str:
        return self.get_status_display()

    @property
    def status_badge_class(self) -> str:
        """Return semantic Bootstrap badge class for the current lead status."""
        badge_map = {
            LeadStatus.NEW: 'bg-primary text-white',
            LeadStatus.CONTACTED: 'bg-info text-dark',
            LeadStatus.FOLLOW_UP: 'bg-warning text-dark',
            LeadStatus.PROPOSAL_SENT: 'bg-secondary text-white',
            LeadStatus.MATURE: 'bg-success text-white',
            LeadStatus.CLOSED: 'bg-dark text-white',
        }
        return badge_map.get(self.status, 'bg-secondary text-white')

    @property
    def tabler_badge_class(self) -> str:
        """Return modern Tabler light badge class for the current lead status."""
        badge_map = {
            LeadStatus.NEW: 'bg-blue-lt',
            LeadStatus.CONTACTED: 'bg-azure-lt',
            LeadStatus.FOLLOW_UP: 'bg-yellow-lt',
            LeadStatus.PROPOSAL_SENT: 'bg-purple-lt',
            LeadStatus.MATURE: 'bg-green-lt',
            LeadStatus.CLOSED: 'bg-secondary-lt',
        }
        return badge_map.get(self.status, 'bg-secondary-lt')

    @property
    def is_follow_up_due(self) -> bool:
        """Check if a follow-up is scheduled and due."""
        from django.utils import timezone
        if not self.follow_up_date:
            return False
        return self.follow_up_date <= timezone.now() and self.status not in (LeadStatus.MATURE, LeadStatus.CLOSED)

    def get_whatsapp_url(self) -> str | None:
        """
        Generate a wa.me URL for the 10-digit Indian mobile number.
        Under documented assignment policy, India country code '91' is prefixed
        to the normalized 10-digit number.
        Returns None if the number is not a valid 10-digit number.
        """
        raw_digits = ''.join(ch for ch in str(self.mobile_number) if ch.isdigit())
        if len(raw_digits) != 10:
            return None

        international_phone = f"91{raw_digits}"
        service_title = self.get_service_display()
        intro_text = (
            f"Hello {self.full_name}, thank you for your interest in {service_title}. "
            f"We received your inquiry (Reference ID: {self.reference_id}). "
            f"Our team would be happy to assist you. Please let us know a convenient time to connect."
        )
        encoded_message = urllib.parse.quote(intro_text)
        return f"https://wa.me/{international_phone}?text={encoded_message}"


class LeadStatusHistory(models.Model):
    """
    Immutable audit history record tracking every status transition
    for an inquiry, recording the acting administrator and timestamp.
    """
    id = models.BigAutoField(primary_key=True)
    inquiry = models.ForeignKey(
        Inquiry,
        on_delete=models.CASCADE,
        related_name='status_history',
        help_text='Inquiry associated with this status transition.'
    )
    previous_status = models.CharField(
        max_length=30,
        choices=LeadStatus.choices,
        help_text='Status prior to transition.'
    )
    new_status = models.CharField(
        max_length=30,
        choices=LeadStatus.choices,
        help_text='New status applied in this transition.'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lead_status_updates',
        help_text='Staff user who performed the status update (preserved if user is deleted).'
    )
    remarks = models.TextField(
        max_length=500,
        blank=True,
        default='',
        help_text='Optional internal remarks or transition notes.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='Exact timestamp when the status transition was recorded.'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Lead Status History'
        verbose_name_plural = 'Lead Status Histories'

    def __str__(self) -> str:
        actor = self.updated_by.username if self.updated_by else 'System'
        return f"{self.inquiry.reference_id}: {self.previous_status} -> {self.new_status} by {actor}"
