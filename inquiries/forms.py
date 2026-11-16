"""
Public inquiry submission form with authoritative server-side validation,
anti-bot honeypot check, and clean input sanitization.
"""
from django import forms
from django.core.exceptions import ValidationError
from inquiries.models import ServiceChoices
from inquiries.validators import validate_mobile_number, validate_full_name


class InquirySubmissionForm(forms.Form):
    """
    Form for prospective clients to submit inquiries on the public portal.
    Enforces strict server-side validation and anti-spam protection.
    """
    full_name = forms.CharField(
        max_length=120,
        required=True,
        validators=[validate_full_name],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name',
            'autocomplete': 'name',
            'required': 'required',
        })
    )
    mobile_number = forms.CharField(
        max_length=10,
        min_length=10,
        required=True,
        validators=[validate_mobile_number],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '10-digit mobile number (e.g. 9876543210)',
            'autocomplete': 'tel',
            'inputmode': 'numeric',
            'pattern': r'\d{10}',
            'maxlength': '10',
            'required': 'required',
        })
    )
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'name@example.com',
            'autocomplete': 'email',
            'required': 'required',
        })
    )
    service = forms.ChoiceField(
        choices=[('', '-- Select a Service --')] + list(ServiceChoices.choices),
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': 'required',
        })
    )
    message = forms.CharField(
        max_length=2000,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Briefly describe your requirements or query (optional, up to 2000 characters)',
        })
    )
    # Anti-bot honeypot field — hidden from normal users via offscreen CSS and tabindex=-1
    website_url = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control-hp',
            'tabindex': '-1',
            'autocomplete': 'off',
            'aria-hidden': 'true',
        })
    )

    def clean_full_name(self) -> str:
        name = self.cleaned_data.get('full_name', '')
        normalized = ' '.join(name.strip().split())
        validate_full_name(normalized)
        return normalized

    def clean_mobile_number(self) -> str:
        mobile = self.cleaned_data.get('mobile_number', '').strip()
        validate_mobile_number(mobile)
        return mobile

    def clean_email(self) -> str:
        email = self.cleaned_data.get('email', '').strip().lower()
        return email

    def clean_service(self) -> str:
        service = self.cleaned_data.get('service', '').strip()
        valid_services = [choice[0] for choice in ServiceChoices.choices]
        if service not in valid_services:
            raise ValidationError('Please select a valid service from the available choices.')
        return service

    def clean_message(self) -> str:
        msg = self.cleaned_data.get('message', '').strip()
        if len(msg) > 2000:
            raise ValidationError('Message must not exceed 2000 characters.')
        return msg

    def clean_website_url(self) -> str:
        val = self.cleaned_data.get('website_url', '').strip()
        if val:
            # Honeypot filled by automated bot
            raise ValidationError('Automated submission detected. Request rejected.')
        return val
