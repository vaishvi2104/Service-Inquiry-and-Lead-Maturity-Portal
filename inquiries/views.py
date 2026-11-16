"""
Public views for Start-Up Sahay customer portal.
Handles landing page, service display, inquiry submission with rate limiting,
honeypot protection, and Post/Redirect/Get confirmation flow.
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from inquiries.forms import InquirySubmissionForm
from inquiries.models import ServiceChoices, Inquiry
from inquiries.services import save_customer_inquiry, check_rate_limit


# Official verified company facts from Start-Up Sahay Private Limited
COMPANY_INFO = {
    'name': 'Start-Up Sahay Private Limited',
    'legal_type': 'Private Limited Consultancy Firm',
    'email': 'info@startupsahay.com',
    'phone': '+91-63526-75546',
    'address': 'B-304, Ganesh Glory 11, Jagatpur Road, Gota, Ahmedabad, Gujarat 382470',
    'website': 'https://www.startupsahay.com/',
    'disclaimer': (
        'Start-Up Sahay Private Limited is an independent professional consultancy and service provider. '
        'We are not affiliated with, authorized by, or a representative of any government department, '
        'regulatory agency, or statutory board. Final approvals, grants, registrations, and certifications '
        'remain solely under the jurisdiction and discretion of the respective competent government authorities.'
    ),
}

# The four mandatory service tracks
SERVICES_LIST = [
    {
        'key': ServiceChoices.COMPANY_INCORPORATION,
        'title': 'Company Incorporation',
        'icon': 'bi-building-check',
        'short_desc': (
            'End-to-end professional assistance with entity structuring, documentation drafting, '
            'and MCA filing for Private Limited, LLP, and OPC registrations.'
        ),
        'disclaimer_note': 'Incorporation approvals are granted solely by the Registrar of Companies (ROC), Ministry of Corporate Affairs.',
    },
    {
        'key': ServiceChoices.DPIIT_RECOGNITION,
        'title': 'Startup India DPIIT Recognition',
        'icon': 'bi-award',
        'short_desc': (
            'Expert consultancy and compliance documentation for eligible startups seeking recognition '
            'under the Department for Promotion of Industry and Internal Trade (DPIIT).'
        ),
        'disclaimer_note': 'Recognition certificates and eligibility determinations remain under the sole purview of DPIIT.',
    },
    {
        'key': ServiceChoices.TRADEMARK_REGISTRATION,
        'title': 'Trademark Registration',
        'icon': 'bi-shield-check',
        'short_desc': (
            'Comprehensive brand name search, class classification analysis, application preparation, '
            'and procedural guidance through trademark registry workflows.'
        ),
        'disclaimer_note': 'Trademark grants and opposition outcomes depend entirely on the Trade Marks Registry.',
    },
    {
        'key': ServiceChoices.SEED_FUND_SUPPORT,
        'title': 'Seed Fund Support',
        'icon': 'bi-cash-coin',
        'short_desc': (
            'Consultative guidance for startup seed-fund application readiness, pitch alignment, '
            'and compliance documentation across eligible incubator frameworks.'
        ),
        'disclaimer_note': 'Seed funding allocation is decided independently by eligible incubators and government committees.',
    },
]


def home_view(request):
    """
    Public landing page presenting company profile, service offerings,
    compliance disclaimers, and the customer inquiry submission form.
    """
    selected_service = request.GET.get('service', '').strip()

    if request.method == 'POST':
        # 1. Rate Limiting Check
        if check_rate_limit(request):
            messages.error(
                request,
                'Submission limit reached. For security, please wait a few minutes before submitting another inquiry.'
            )
            form = InquirySubmissionForm(request.POST)
            return render(request, 'public/home.html', {
                'form': form,
                'company': COMPANY_INFO,
                'services': SERVICES_LIST,
            })

        form = InquirySubmissionForm(request.POST)
        if form.is_valid():
            inquiry = save_customer_inquiry(form.cleaned_data)
            # Store reference ID safely in session for confirmation display
            request.session['inquiry_success_ref'] = inquiry.reference_id
            request.session['inquiry_success_service'] = inquiry.get_service_display()
            # Post/Redirect/Get prevents duplicate form submission
            return redirect('public:success')
        else:
            messages.error(request, 'Please correct the highlighted errors in the form.')
    else:
        initial_data = {}
        if selected_service in dict(ServiceChoices.choices):
            initial_data['service'] = selected_service
        form = InquirySubmissionForm(initial=initial_data)

    return render(request, 'public/home.html', {
        'form': form,
        'company': COMPANY_INFO,
        'services': SERVICES_LIST,
    })


def inquiry_success_view(request):
    """
    Confirmation page displayed after a successful inquiry submission.
    Provides reference ID without exposing internal database keys.
    """
    ref_id = request.session.pop('inquiry_success_ref', None)
    service_name = request.session.pop('inquiry_success_service', None)

    # If accessed directly without a recent submission, retrieve through safe query param or redirect
    if not ref_id:
        param_ref = request.GET.get('ref', '').strip()
        if param_ref and Inquiry.objects.filter(reference_id=param_ref).exists():
            inquiry = Inquiry.objects.get(reference_id=param_ref)
            ref_id = inquiry.reference_id
            service_name = inquiry.get_service_display()
        else:
            return redirect('public:home')

    return render(request, 'public/inquiry_success.html', {
        'reference_id': ref_id,
        'service_name': service_name,
        'company': COMPANY_INFO,
    })
