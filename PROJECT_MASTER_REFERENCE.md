# Start-Up Sahay Private Limited — Project Master Reference Manual

> **Purpose:** Comprehensive, single-source reference manual documenting all architectural decisions, database models, security controls, public portal features, admin dashboard workflows, test verification, and operational commands for the **Start-Up Sahay Service Inquiry & Lead Maturity Portal**.

---

## 1. Project Overview & Business Domain

* **Organization:** **Start-Up Sahay Private Limited**
* **Nature of Business:** Independent corporate consultancy and advisory services firm headquartered in Ahmedabad, Gujarat.
* **Statutory Compliance:** Private Limited entity; strictly **not affiliated with, authorized by, or a representative of any government department, regulatory agency, or statutory board**. All statutory approvals (e.g., ROC incorporation, DPIIT recognition, Trademark grants, Seed Fund allocations) remain solely under the purview and discretion of the competent government authorities.
* **Project Directory:** `C:\Users\VAISHVI SHAH\.gemini\antigravity\scratch\startupsahay-portal`
* **Technology Stack:**
  * **Backend:** Python 3.12, Django 5.2.5 (ORM, templates, forms, auth, sessions, messages).
  * **Database:** SQLite (relational schema with indexes, transactions, and foreign key constraints; PostgreSQL-ready).
  * **Frontend:** HTML5, CSS3, Vanilla JavaScript (zero TypeScript, zero framework dependencies), Bootstrap 5.3, Bootstrap Icons 1.11.
  * **Environment Management:** Hybrid environment loader supporting `python-dotenv` and standard library fallback.

---

## 2. Complete Project Directory Structure

```text
startupsahay-portal/
├── manage.py                                 # Django CLI runner
├── requirements.txt                          # Production & local dependencies
├── .env.example                              # Safe environment variable template
├── .env                                      # Local development settings (git-ignored)
├── .gitignore                                # Comprehensive version control exclusion rules
├── README.md                                 # Standard GitHub / evaluator overview
├── PROJECT_MASTER_REFERENCE.md               # Master reference manual (this document)
├── FINAL_ASSIGNMENT_AUDIT_REPORT.md          # Acceptance audit report with verification evidence
├── config/
│   ├── __init__.py
│   ├── env.py                                # Hybrid environment loader with standard-library fallback
│   ├── settings.py                           # Application settings & security configurations
│   ├── urls.py                               # Root URL dispatcher
│   ├── wsgi.py                               # WSGI application entrypoint
│   └── asgi.py                               # ASGI application entrypoint
├── inquiries/
│   ├── migrations/
│   │   ├── 0001_initial.py                   # Initial database migration
│   │   └── __init__.py
│   ├── __init__.py
│   ├── admin.py                              # Django Admin model registrations
│   ├── apps.py                               # App configuration
│   ├── forms.py                              # InquirySubmissionForm with honeypot & server validation
│   ├── models.py                             # Inquiry & LeadStatusHistory models
│   ├── services.py                           # Collision-resistant reference ID, rate-limiting, persistence
│   ├── validators.py                         # Strict name & 10-digit mobile number validators
│   ├── urls.py                               # Public routes ('', 'inquiry/success/')
│   ├── views.py                              # home_view and inquiry_success_view
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py                    # Model constraints, WhatsApp URL, string representation
│       ├── test_forms.py                     # Form validations, honeypot, overlong text, mobile checks
│       └── test_public_views.py              # Public page rendering, PRG submission, XSS prevention
├── dashboard/
│   ├── migrations/
│   │   └── __init__.py
│   ├── templatetags/
│   │   ├── __init__.py
│   │   └── dashboard_tags.py                 # Query string transform tag for preserving filters in pagination
│   ├── __init__.py
│   ├── admin.py                              # Dashboard admin configuration
│   ├── apps.py                               # App configuration
│   ├── forms.py                              # StaffLoginForm and LeadStatusUpdateForm
│   ├── services.py                           # Metric aggregation, parameterized search/filter, atomic update
│   ├── urls.py                               # Protected admin routes (login, logout, overview, leads, detail)
│   ├── views.py                              # staff_required views, authentication, status transitions
│   └── tests/
│       ├── __init__.py
│       ├── test_auth.py                      # Anonymous redirection, staff permissions, safe logout
│       ├── test_leads.py                     # Search, filter, pagination, atomic status transitions
│       └── test_security.py                  # CSRF enforcement, SQL injection immunity, output escaping
├── templates/
│   ├── base.html                             # Base template with Bootstrap 5 and semantic landmarks
│   ├── includes/
│   │   ├── messages.html                     # Dismissible Bootstrap alert banners
│   │   ├── public_navbar.html                # Responsive header with smooth navigation
│   │   └── dashboard_sidebar.html            # Staff navigation sidebar with active user info & logout
│   ├── public/
│   │   ├── home.html                         # Public landing page, 4 services, disclaimer, inquiry form
│   │   └── inquiry_success.html              # Reference ID confirmation with copy-to-clipboard button
│   └── dashboard/
│       ├── login.html                        # Secure staff login page
│       ├── overview.html                     # Metric aggregation cards & recent leads table
│       ├── leads.html                        # Lead directory with search, filter, and pagination
│       └── lead_detail.html                  # Lead profile, message, WhatsApp action, audit history
├── static/
│   ├── css/
│   │   ├── style.css                         # Scoped public portal styles (zero destructive overrides)
│   │   └── dashboard.css                     # Corporate CRM & timeline styles
│   ├── js/
│   │   ├── main.js                           # Vanilla JS: input masking, service selector, clipboard copy
│   │   └── dashboard.js                      # Vanilla JS: alert auto-dismiss, UI helpers
│   └── images/
└── docs/
    ├── SECURITY_REVIEW.md                    # In-depth security analysis and threat review
    └── AI_CHAT_HISTORY.md                    # Authentic AI development history & transcript access
```

---

## 3. Database Schema & Data Models

### 3.1 Model: `Inquiry` (Table: `inquiries_inquiry`)

| Column Name | Type | Constraints / Attributes | Description |
| :--- | :--- | :--- | :--- |
| `id` | BigAutoField | Primary Key | Internal database identifier. |
| `reference_id` | CharField(24) | Unique, Indexed, Non-editable | Public collision-resistant reference ID (e.g. `SS-20261116-A8F2`). |
| `full_name` | CharField(120) | Required, Validated | Customer's full contact name. Validated against control characters and malicious symbols. |
| `mobile_number` | CharField(10) | Required, Indexed, Validated | Exactly 10 ASCII numeric digits (Indian mobile standard). |
| `email` | EmailField(254) | Required, Indexed | Primary customer email address. |
| `service` | CharField(40) | Required, Choices, Indexed | One of 4 predefined service choices. |
| `message` | TextField(2000)| Blankable, Max Length 2000 | Customer inquiry description. Rendered with template autoescaping. |
| `status` | CharField(30) | Required, Choices, Indexed, Default=`new` | Current lead maturity stage. |
| `created_at` | DateTimeField | Auto-now-add, Indexed | Submission timestamp. |
| `updated_at` | DateTimeField | Auto-now | Timestamp of last status modification. |

**Indexes Defined:**
* `inquiry_status_created_idx`: Composite index on `['status', '-created_at']` for high-speed dashboard filtering.
* `inquiry_mobile_status_idx`: Composite index on `['mobile_number', 'status']` for rapid customer search.
* `inquiry_ref_id_idx`: Index on `['reference_id']` for immediate detail lookup.

### 3.2 Model: `LeadStatusHistory` (Table: `inquiries_leadstatushistory`)

| Column Name | Type | Constraints / Attributes | Description |
| :--- | :--- | :--- | :--- |
| `id` | BigAutoField | Primary Key | History record primary key. |
| `inquiry_id` | ForeignKey | `on_delete=CASCADE` | Related inquiry. If an inquiry is purged, its audit trail purges with it. |
| `previous_status` | CharField(30) | Choices | Stage prior to update. |
| `new_status` | CharField(30) | Choices | Newly applied stage. |
| `updated_by_id` | ForeignKey | `on_delete=SET_NULL`, Nullable | Staff user who performed the update. Preserved if staff user account is removed. |
| `remarks` | TextField(500) | Blankable, Max Length 500 | Optional internal transition notes. |
| `created_at` | DateTimeField | Auto-now-add, Indexed | Exact timestamp of the status transition. |

---

## 4. The Six Lead Workflow Stages

The lead maturity pipeline strictly uses the 6 required stages:

1. **New Inquiry (`new`)**: Default stage applied immediately upon customer submission.
2. **Contacted (`contacted`)**: Initial outreach initiated by staff via telephone, email, or WhatsApp.
3. **Follow-up (`follow_up`)**: Ongoing requirement gathering or scheduled consultation calls.
4. **Proposal Sent (`proposal_sent`)**: Quotation, service scope, and checklist delivered to prospective client.
5. **Mature (`mature`)**: Prospect has agreed to terms and is qualified for formal engagement.
6. **Closed (`closed`)**: Engagement completed, onboarding finalized, or inquiry archived.

### Atomic Status Update & No-Op Policy
* All status transitions require a secure **POST** request with CSRF protection.
* The acting staff user is derived strictly from `request.user` (never accepted from client form data).
* Updates run inside `transaction.atomic()` with `Inquiry.objects.select_for_update().get(...)` to prevent concurrency collisions.
* **Documented No-Op Policy:** If the requested `new_status` is identical to the current `status`, the operation is rejected with an informational warning ("Inquiry is already in this status. No changes made."), and no redundant history record is inserted.

---

## 5. The Four Required Services & Copy Guidelines

1. **Company Incorporation (`company_incorporation`)**:
   * *Description:* Professional assistance with structuring, drafting documents, and filing for Private Limited, LLP, and OPC entities under the MCA.
   * *Statutory Disclaimer:* Approvals are granted solely by the Registrar of Companies (ROC), Ministry of Corporate Affairs.
2. **Startup India DPIIT Recognition (`dpiit_recognition`)**:
   * *Description:* Consultancy and compliance documentation for eligible startups seeking DPIIT recognition.
   * *Statutory Disclaimer:* Certificates and tax exemption eligibility are granted solely by DPIIT.
3. **Trademark Registration (`trademark_registration`)**:
   * *Description:* Comprehensive brand search, Nice classification guidance, and filing documentation support.
   * *Statutory Disclaimer:* Trademark registration is granted solely by the Trade Marks Registry.
4. **Seed Fund Support (`seed_fund_support`)**:
   * *Description:* Guidance on application readiness, pitch presentation structuring, and compliance alignment.
   * *Statutory Disclaimer:* Seed funding grants are disbursed solely by approved incubators and government committees.

---

## 6. WhatsApp Direct Outreach Integration

* **Standard Format:** `https://wa.me/91{10_DIGIT_PHONE}?text={ENCODED_MESSAGE}`
* **Country Code Policy:** Under the assignment specification for Indian mobile numbers, country code `91` is prefixed to the normalized 10-digit number.
* **Prefilled Template:**
  > "Hello [Customer Name], thank you for your interest in [Selected Service]. We received your inquiry (Reference ID: [Reference ID]). Our team would be happy to assist you. Please let us know a convenient time to connect."
* **Security & Fallback:**
  * Opens in a new tab with `target="_blank" rel="noopener noreferrer"`.
  * If the mobile number does not consist of exactly 10 digits, the WhatsApp button is rendered in a clear disabled/unavailable state (`get_whatsapp_url()` returns `None`).

---

## 7. Security Architecture & Controls

1. **Role-Based Authorization:**
   * Every administrative view is protected by `@staff_required`.
   * Unauthenticated visitors are redirected to `/dashboard/login/?next=...`.
   * Authenticated non-staff users receive HTTP 403 Forbidden.
2. **Spam & Abuse Protection:**
   * **Honeypot:** Hidden field `website_url` styled offscreen. Any automated bot that populates this field is rejected immediately with zero database writes.
   * **Rate Limiting:** Public inquiry submissions throttled by client IP (configurable via `INQUIRY_RATE_LIMIT_MAX_REQUESTS=5` and `INQUIRY_RATE_LIMIT_WINDOW_SECONDS=600`).
3. **Cross-Site Request Forgery (CSRF):**
   * `CsrfViewMiddleware` active globally.
   * `{% csrf_token %}` included in every state-changing form.
   * Logout and status updates strictly enforce `POST` (rejecting `GET` with HTTP 405).
4. **Cross-Site Scripting (XSS):**
   * Template autoescaping active; customer message rendered as plain text.
   * Vanilla JS uses `textContent` exclusively (no `innerHTML`).
5. **SQL Injection (SQLi):**
   * 100% ORM parameterized queries (`Q` objects); zero raw SQL.
6. **Session & Cookie Hardening:**
   * `SESSION_COOKIE_HTTPONLY = True`
   * `CSRF_COOKIE_HTTPONLY = True`
   * `SESSION_COOKIE_SAMESITE = 'Lax'`
   * `CSRF_COOKIE_SAMESITE = 'Lax'`

---

## 8. Automated Testing Evidence (51 Tests + 10 E2E Browser Steps)

```text
Ran 51 tests in 23.698s
OK (0 failures, 0 errors, 0 skips)
```

### Live Browser End-to-End Verification (10 / 10 Steps Passed)
* **Step 1:** Public Homepage loaded, verified brand title, hero headline, 4 service cards, and mandatory statutory disclaimer.
* **Step 2:** "Enquire Now" button clicked on Company Incorporation card; verified smooth-scroll and dropdown auto-selection (`company_incorporation`).
* **Step 3:** Filled public inquiry form for "Vaishvi Shah" (`9876543210`, `vaishvi@example.com`); verified CSRF and client numeric masking; submitted form.
* **Step 4:** Redirection to confirmation page via Post/Redirect/Get; generated reference ID `SS-20261116-D9AF` displayed; verified copy-to-clipboard button.
* **Step 5:** Accessed `/dashboard/`; unauthenticated access safely redirected to `/dashboard/login/?next=/dashboard/`; authenticated using staff credentials (`admin` / `AdminPassword123!`).
* **Step 6:** Executive overview verified; dynamic metrics calculated; submitted lead `SS-20261116-D9AF` confirmed in recent inquiries table.
* **Step 7:** Customer leads directory search tested with query "Vaishvi"; verified search filter cleanly isolated the target record.
* **Step 8:** Lead detail page inspected; customer message displayed safely escaped; prefilled WhatsApp action verified (`wa.me/919876543210?text=...`).
* **Step 9:** Atomic status transition executed: advanced stage to "Contacted", entered audit remarks; verified success alert banner, status badge updated to "Contacted", and stage transition timeline recorded previous/new status, `admin` actor, remarks, and timestamp.
* **Step 10:** Logout executed via POST; verified session invalidation and redirection to login page.

### Breakdown of Unit & Integration Test Suites
* **`inquiries/tests/test_models.py` (7 tests):**
  1. `test_inquiry_string_representation` — PASS
  2. `test_default_status_is_new` — PASS
  3. `test_whatsapp_url_generation_for_valid_number` — PASS
  4. `test_whatsapp_url_returns_none_for_invalid_number` — PASS
  5. `test_status_badge_classes` — PASS
  6. `test_lead_status_history_cascade` — PASS
  7. `test_lead_status_history_user_set_null` — PASS
* **`inquiries/tests/test_forms.py` (10 tests):**
  8. `test_valid_form_submission` — PASS
  9. `test_blank_required_fields_rejected` — PASS
  10. `test_invalid_mobile_number_short` — PASS
  11. `test_invalid_mobile_number_with_country_code` — PASS
  12. `test_invalid_mobile_number_alphanumeric` — PASS
  13. `test_invalid_email_format` — PASS
  14. `test_unknown_service_choice_rejected` — PASS
  15. `test_overlong_message_rejected` — PASS
  16. `test_honeypot_filled_causes_rejection` — PASS
  17. `test_name_whitespace_normalized` — PASS
* **`inquiries/tests/test_public_views.py` (8 tests):**
  18. `test_homepage_loads` — PASS
  19. `test_all_four_required_services_present` — PASS
  20. `test_disclaimer_rendered` — PASS
  21. `test_valid_inquiry_submission_persists_and_redirects` — PASS
  22. `test_success_page_displays_reference_id` — PASS
  23. `test_success_page_direct_access_without_session_redirects` — PASS
  24. `test_honeypot_submission_does_not_create_inquiry` — PASS
  25. `test_xss_in_message_is_escaped` — PASS
* **`dashboard/tests/test_auth.py` (10 tests):**
  26. `test_anonymous_access_to_overview_redirects_to_login` — PASS
  27. `test_anonymous_access_to_leads_redirects_to_login` — PASS
  28. `test_anonymous_access_to_lead_detail_redirects_to_login` — PASS
  29. `test_anonymous_access_to_status_update_redirects_to_login` — PASS
  30. `test_authenticated_non_staff_user_denied_forbidden` — PASS
  31. `test_valid_staff_login_succeeds` — PASS
  32. `test_invalid_login_fails_safely` — PASS
  33. `test_logout_via_get_method_rejected` — PASS
  34. `test_logout_via_post_succeeds_and_invalidates_session` — PASS
  35. `test_no_public_admin_registration_endpoint` — PASS
* **`dashboard/tests/test_leads.py` (10 tests):**
  36. `test_overview_metrics_aggregation` — PASS
  37. `test_leads_ordered_newest_first` — PASS
  38. `test_search_by_name` — PASS
  39. `test_search_by_phone` — PASS
  40. `test_search_by_reference_id` — PASS
  41. `test_filter_by_status` — PASS
  42. `test_search_and_status_combined` — PASS
  43. `test_valid_status_transition_succeeds_and_creates_history` — PASS
  44. `test_no_op_same_status_update_rejected` — PASS
  45. `test_invalid_status_value_rejected` — PASS
* **`dashboard/tests/test_security.py` (6 tests):**
  46. `test_csrf_protection_enforced_on_status_update` — PASS
  47. `test_csrf_protection_enforced_on_logout` — PASS
  48. `test_get_request_cannot_change_lead_status` — PASS
  49. `test_sql_injection_probe_strings_handled_safely` — PASS
  50. `test_template_autoescaping_prevents_xss` — PASS
  51. `test_security_cookie_configurations` — PASS

---

## 9. Windows & Linux Operational Commands

### 9.1 Windows (PowerShell)

```powershell
# 1. Navigate to project directory
cd "C:\Users\VAISHVI SHAH\.gemini\antigravity\scratch\startupsahay-portal"

# 2. (Optional) Create & activate a virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install requirements
pip install -r requirements.txt

# 4. Initialize environment variables from template
Copy-Item .env.example .env

# 5. Run migrations
python manage.py migrate

# 6. Create initial administrator / staff account
python manage.py createsuperuser

# 7. Execute automated test suite
python manage.py test -v 2

# 8. Start development server
python manage.py runserver
```

### 9.2 macOS / Linux (Bash)

```bash
# 1. Navigate to project directory
cd startupsahay-portal

# 2. Create & activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install requirements
pip install -r requirements.txt

# 4. Initialize environment variables
cp .env.example .env

# 5. Run migrations
python3 manage.py migrate

# 6. Create initial administrator account
python3 manage.py createsuperuser

# 7. Execute automated test suite
python3 manage.py test -v 2

# 8. Start development server
python3 manage.py runserver
```

---

## 10. Accessing the Authentic AI Trajectory

The complete machine-generated conversation history is preserved on disk:
* **Transcript:** `C:\Users\VAISHVI SHAH\.gemini\antigravity\brain\73b26742-8e19-44e8-90c1-aa58fee1e77d\.system_generated\logs\transcript.jsonl`
* **Conversation ID:** `73b26742-8e19-44e8-90c1-aa58fee1e77d`
