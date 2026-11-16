# Start-Up Sahay Private Limited — Project Master Reference Manual

> **Purpose:** Comprehensive, single-source reference manual documenting all architectural decisions, database models, security controls, public portal features, admin dashboard workflows, test verification, and operational commands for the **Start-Up Sahay Service Inquiry & Lead Maturity Portal**.

---

## 1. Project Overview & Business Domain

* **Organization:** **Start-Up Sahay Private Limited**
* **Nature of Business:** Independent corporate consultancy and advisory services firm headquartered in Ahmedabad, Gujarat.
* **Statutory Compliance:** Private Limited entity; strictly **not affiliated with, authorized by, or a representative of any government department, regulatory agency, or statutory board**. All statutory approvals (e.g., ROC incorporation, DPIIT recognition, Trademark grants, Seed Fund allocations) remain solely under the purview and discretion of the competent government authorities.
* **Project Directory:** `startupsahay-portal/`
* **Application Name:** **Sahay LeadFlow Portal**
* **Repository:** `Service-Inquiry-and-Lead-Maturity-Portal`
* **Technology Stack:**
  * **Backend:** Python 3.12, Django 5.2.5 (ORM, templates, forms, auth, sessions, messages).
  * **Database:** SQLite (relational schema with indexes, transactions, and foreign key constraints; PostgreSQL-ready).
  * **Frontend (Admin Portal):** Official **Tabler UI** (`@tabler/core` 1.6.1), Tabler Icons (`@tabler/icons-webfont`), ApexCharts (MIT), Dark/Light mode theme engine, zero frontend framework build dependency.
  * **Frontend (Public Portal):** Dedicated clean corporate landing page using custom modular CSS (`static/css/style.css`), Vanilla JavaScript, responsive service cards, and anti-bot protections.
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
│   ├── urls.py                               # Protected admin routes (overview, leads, detail, kanban, follow-ups, etc.)
│   ├── views.py                              # staff_required views, authentication, status transitions
│   └── tests/
│       ├── __init__.py
│       ├── test_auth.py                      # Anonymous redirection, staff permissions, safe logout
│       ├── test_leads.py                     # Search, filter, pagination, atomic status transitions
│       ├── test_security.py                  # CSRF enforcement, SQL injection immunity, output escaping
│       └── test_tabler_features.py           # Kanban, follow-ups, lead create/edit, CSV export, profile
├── templates/
│   ├── base.html                             # Base template for public portal with semantic landmarks
│   ├── tabler_base.html                      # Primary Tabler admin dashboard base layout
│   ├── includes/
│   │   ├── messages.html                     # Public dismissible Bootstrap alert banners
│   │   ├── public_navbar.html                # Responsive public header with smooth navigation
│   │   ├── tabler_sidebar.html               # Tabler sidebar navigation with active highlights
│   │   ├── tabler_header.html                # Tabler top bar with dark mode toggle & user menu
│   │   └── tabler_messages.html              # Tabler dismissible alert toasts
│   ├── public/
│   │   ├── home.html                         # Public landing page, 4 services, disclaimer, inquiry form
│   │   └── inquiry_success.html              # Reference ID confirmation with copy-to-clipboard button
│   └── dashboard/
│       ├── login.html                        # Tabler Admin Login page
│       ├── overview.html                     # Tabler Main Dashboard (8 KPIs + 2 ApexCharts + Recent Leads)
│       ├── leads.html                        # Tabler All Inquiries / Leads (Filters, pagination, CSV)
│       ├── lead_detail.html                  # Tabler Lead Details (Datagrid, WhatsApp, status update, timeline)
│       ├── lead_form.html                    # Tabler Add / Edit Lead Form
│       ├── kanban.html                       # Tabler Lead Pipeline / 6-Stage Kanban Board
│       ├── follow_ups.html                   # Tabler Follow-up Management Desk (Overdue, Due Today, Upcoming)
│       ├── status_history.html               # Tabler Lead Status History Full Audit Trail
│       ├── advanced_search.html              # Tabler Search & Advanced Query Builder
│       └── profile.html                      # Tabler Admin Profile, Password Change & System Settings
├── static/
│   ├── tabler/                               # Official pinned Tabler Core assets (v1.6.1)
│   │   ├── css/                              # tabler.min.css, tabler-icons.min.css, 48 offline woff2 fonts
│   │   ├── js/                               # tabler.min.js, apexcharts.min.js
│   │   └── LICENSE.md                        # Dependency licenses (MIT)
│   ├── css/
│   │   ├── style.css                         # Scoped public portal styles (zero destructive overrides)
│   │   └── dashboard.css                     # Minimal Tabler enhancements
│   ├── js/
│   │   ├── main.js                           # Vanilla JS: input masking, service selector, clipboard copy
│   │   └── dashboard.js                      # Vanilla JS: Tabler theme initialization, alert helpers
│   └── images/
│       └── tabler_screenshots/               # 12 Full-page browser test capture PNGs
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

## 8. Automated Testing Evidence (63 Tests + 12 Tabler Live Browser Pages)

```text
Ran 63 tests in 39.620s
OK (63 passed, 0 failures, 0 errors, 0 skips)
```

### Tabler UI Live Browser Verification (12 / 12 Pages Verified)
* **Page 1:** Public Corporate Website (`/`)
* **Page 2:** Tabler Admin Login (`/dashboard/login/`)
* **Page 3:** Main Dashboard with 8 KPI cards & ApexCharts (`/dashboard/`)
* **Page 4:** All Inquiries / Leads Directory with filters (`/dashboard/leads/`)
* **Page 5:** Lead Details with WhatsApp button & status update (`/dashboard/leads/<ref>/`)
* **Page 6:** Add New Lead Form (`/dashboard/leads/create/`)
* **Page 7:** Lead Pipeline / 6-Stage Kanban Board (`/dashboard/kanban/`)
* **Page 8:** Follow-up Management Desk (`/dashboard/follow-ups/`)
* **Page 9:** Lead Status History Audit Log (`/dashboard/history/`)
* **Page 10:** Advanced Search & Query Builder with CSV Export (`/dashboard/search/`)
* **Page 11:** Admin Profile & System Settings (`/dashboard/profile/`)
* **Page 12:** Tabler Dark Mode Switch (`data-bs-theme="dark"`)

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
* **`dashboard/tests/test_tabler_features.py` (12 tests):**
  52. `test_kanban_view_renders_all_six_columns` — PASS
  53. `test_kanban_move_updates_stage_and_creates_history` — PASS
  54. `test_follow_ups_view_renders_categories` — PASS
  55. `test_schedule_follow_up_action` — PASS
  56. `test_lead_create_view_creates_inquiry_and_history` — PASS
  57. `test_lead_edit_view_updates_fields` — PASS
  58. `test_status_history_view_renders_and_filters` — PASS
  59. `test_advanced_search_view_filters_and_renders` — PASS
  60. `test_csv_export_returns_csv_file` — PASS
  61. `test_profile_view_renders_user_data` — PASS
  62. `test_profile_update_changes_name` — PASS
  63. `test_all_tabler_pages_require_staff_auth` — PASS

### 8.4 Comprehensive Visible Live Browser Field Verification (22 / 22 Steps Verified)

Executed live against `http://127.0.0.1:8000/` using Playwright Chromium with visual animation (`slow_mo=600`) directly on the Windows interactive desktop:

| Step # | Field / Workflow Tested | Verification Action | Result |
| :---: | :--- | :--- | :---: |
| 1 | Public Advisory Services | 4 service cards (*Company Incorporation, DPIIT, Trademark, Seed Fund*) verified present | **PASS** |
| 2 | Public Form Controls Presence | Full Name, Mobile, Email, Service dropdown, Message, Honeypot input controls verified | **PASS** |
| 3 | Public Required Field Validation | Blank form submission intercepted by HTML5 validation (`valueMissing=true`) | **PASS** |
| 4 | Mobile Regex Validation | Submitting 5-digit number triggers regex constraint (`patternMismatch=true`) | **PASS** |
| 5 | Public Inquiry Submission | Valid customer form submitted; persisted to SQLite and redirected to `/inquiry/success/` with unique Reference ID (`SS-YYYYMMDD-XXXX`) | **PASS** |
| 6 | Staff Invalid Auth Handling | Invalid password rejected with dismissible `.alert-danger` banner | **PASS** |
| 7 | Staff Valid Authentication | `admin` / `AdminPassword123!` authenticated and redirected to `/dashboard/` | **PASS** |
| 8 | Dashboard KPI Cards & Charts | 8 KPI cards verified; 2 ApexCharts containers (`#chart-stage-distribution`, `#chart-service-breakdown`) loaded | **PASS** |
| 9 | Recent Inquiries Desk | Real-time database query verified; newly submitted lead displayed in recent activity table | **PASS** |
| 10 | Leads Search Input Field | Keyword search by customer name filters directory to matching records | **PASS** |
| 11 | Leads Stage Filter Dropdown | Selecting stage `new` filters query to only New Inquiries | **PASS** |
| 12 | Leads Directory CSV Export | Filter preservation and CSV export link verified | **PASS** |
| 13 | Add Lead Form (`/leads/create/`) | Filled all 8 administrative fields; created new walk-in lead with immediate audit history generation | **PASS** |
| 14 | Lead Detail Datagrid & WhatsApp | Verified Datagrid customer attributes and WhatsApp direct outreach CTA (`https://wa.me/91...`) | **PASS** |
| 15 | Stage Update & Audit History | Updated stage to *Proposal Sent* with custom remarks; audit trail recorded acting staff user and timestamp | **PASS** |
| 16 | Follow-up Date/Time Scheduler | Scheduled consultation for lead; datetime and objective saved | **PASS** |
| 17 | Kanban 6-Stage Pipeline Board | Verified all 6 Kanban columns; card moved to *Mature* column via quick action menu | **PASS** |
| 18 | Follow-up Desk Queues | Verified *Overdue*, *Due Today*, *Upcoming*, and *Unscheduled* queues | **PASS** |
| 19 | Lead Status History Audit Log | Filtered global audit trail by Lead Reference ID | **PASS** |
| 20 | Advanced Search & Query Builder | Multi-criteria search (keyword + service track) filtered records accurately | **PASS** |
| 21 | Admin Profile Name Fields | Updated staff first and last names in user profile; changes persisted to User model | **PASS** |
| 22 | Tabler Dark Mode Switch | Toggled theme engine; attribute `data-bs-theme="dark"` applied cleanly | **PASS** |

---

## 9. Windows & Linux Operational Commands

### 9.1 Windows (PowerShell)

```powershell
# 1. Navigate to project directory
cd startupsahay-portal

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

## 10. Authentic AI Development Disclosure

AI tools were used during development for assistance with implementation, debugging, documentation, and code review.

The development workflow, architectural decisions, and verification results are documented in:
* **Development History:** [docs/AI_CHAT_HISTORY.md](docs/AI_CHAT_HISTORY.md)
* **Conversation Session ID:** `73b26742-8e19-44e8-90c1-aa58fee1e77d`
