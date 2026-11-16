"""
Forms for the staff management dashboard.
Includes secure login and atomic lead status update forms.
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from inquiries.models import LeadStatus


class StaffLoginForm(AuthenticationForm):
    """
    Styled login form for staff authentication.
    Applies Bootstrap classes and security attributes.
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username',
            'autocomplete': 'username',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
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
            'placeholder': 'Optional internal notes explaining this status update (up to 500 characters)',
        })
    )

    def clean_remarks(self) -> str:
        remarks = self.cleaned_data.get('remarks', '').strip()
        if len(remarks) > 500:
            raise forms.ValidationError('Remarks cannot exceed 500 characters.')
        return remarks
