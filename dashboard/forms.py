"""
Forms for the staff management dashboard.
Includes secure login, lead creation/editing, follow-up scheduling, and profile settings.
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import get_user_model
from inquiries.models import Inquiry, LeadStatus, ServiceChoices
from inquiries.validators import validate_mobile_number, validate_full_name

User = get_user_model()


class StaffLoginForm(AuthenticationForm):
    """
    Login form for staff authentication with clear styling.
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username',
            'autocomplete': 'username',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password',
            'autocomplete': 'current-password',
        })
    )


class LeadStatusUpdateForm(forms.Form):
    """
    Form for updating an inquiry's status stage along with optional remarks.
    """
    new_status = forms.ChoiceField(
        choices=LeadStatus.choices,
        widget=forms.Select(attrs={
            'class': 'form-select',
        })
    )
    remarks = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Add internal notes or customer conversation context (up to 500 characters)',
        })
    )

    def clean_remarks(self) -> str:
        remarks = self.cleaned_data.get('remarks', '').strip()
        if len(remarks) > 500:
            raise forms.ValidationError('Remarks cannot exceed 500 characters.')
        return remarks


class LeadForm(forms.ModelForm):
    """
    Form for creating new leads manually by staff and editing existing leads.
    Enforces business validation and state machine rules on status updates.
    """
    class Meta:
        model = Inquiry
        fields = [
            'full_name',
            'mobile_number',
            'email',
            'service',
            'status',
            'follow_up_date',
            'internal_notes',
            'message',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full legal or business name'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10-digit mobile (e.g. 9876543210)', 'maxlength': '10'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'client@example.com'}),
            'service': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'follow_up_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'internal_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Internal strategy, client budget, or requirements (max 2000 characters)'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Customer query / requirement description'}),
        }

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
        return self.cleaned_data.get('email', '').strip().lower()

    def clean_internal_notes(self) -> str:
        notes = self.cleaned_data.get('internal_notes', '').strip()
        if len(notes) > 2000:
            raise forms.ValidationError('Internal notes cannot exceed 2000 characters.')
        return notes

    def clean(self):
        cleaned_data = super().clean()
        new_status = cleaned_data.get('status')
        if self.instance and self.instance.pk and new_status:
            if self.instance.status != new_status:
                from dashboard.services import is_valid_status_transition
                if not is_valid_status_transition(self.instance.status, new_status):
                    target_label = dict(LeadStatus.choices).get(new_status, new_status)
                    self.add_error(
                        'status',
                        f'Cannot transition lead from "{self.instance.get_status_display()}" to "{target_label}".'
                    )
        return cleaned_data


class FollowUpScheduleForm(forms.Form):
    """
    Form for scheduling or updating a follow-up date and adding follow-up remarks.
    """
    follow_up_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        required=True
    )
    remarks = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Follow-up objective or discussion summary (e.g., Send revised quote, demo call)'
        })
    )

    def clean_remarks(self) -> str:
        remarks = self.cleaned_data.get('remarks', '').strip()
        if len(remarks) > 500:
            raise forms.ValidationError('Follow-up remarks cannot exceed 500 characters.')
        return remarks


class AdminProfileForm(forms.ModelForm):
    """
    Form for staff users to update their profile information.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
