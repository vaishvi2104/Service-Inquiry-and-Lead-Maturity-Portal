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
  * **Frontend (Admin Portal):** Enterprise **AdminLTE 4** Design System (Bootstrap 5.3 + Bootstrap Icons), ApexCharts, dark/light theme support, zero frontend build overhead.
  * **Frontend (Public Portal):** Dedicated clean corporate landing page using custom modular CSS (`static/css/style.css`), Vanilla JavaScript, responsive service cards, and anti-bot protections.
  * **Environment Management:** Robust environment loader supporting `python-dotenv` and standard library fallback.

---

## 2. Complete Project Directory Structure

```text
startupsahay-portal/
├── manage.py                                 # Django CLI runner
├── requirements.txt                          # Production & local dependencies (PostgreSQL, Redis support)
├── .env.example                              # Safe environment variable template with full configuration
├── .env                                      # Local development settings (git-ignored)
├── .gitignore                                # Comprehensive version control exclusion rules
├── build.sh                                  # Idempotent production build & deployment script
├── README.md                                 # Canonical project documentation & setup manual
├── PROJECT_MASTER_REFERENCE.md               # Master reference manual (this document)
├── FINAL_ASSIGNMENT_AUDIT_REPORT.md          # Acceptance audit report with verification evidence
├── config/
│   ├── __init__.py
│   ├── env.py                                # Hybrid environment loader with standard-library fallback
│   ├── settings.py                           # Production-hardened settings (PostgreSQL, SSL, Cookies, Redis)
│   ├── urls.py                               # Root URL dispatcher
│   ├── wsgi.py                               # WSGI application entrypoint
│   └── asgi.py                               # ASGI application entrypoint
├── inquiries/
│   ├── migrations/
│   │   ├── 0001_initial.py                   # Initial database migration
│   │   ├── 0002_inquiry_assigned_to_inquiry_follow_up_date_and_more.py
│   │   ├── 0003_followupnote.py              # FollowUpNote model migration
│   │   └── __init__.py
│   ├── __init__.py
│   ├── admin.py                              # Django Admin model registrations & inlines
│   ├── apps.py                               # App configuration
│   ├── forms.py                              # InquirySubmissionForm with honeypot & server validation
│   ├── models.py                             # Inquiry, LeadStatusHistory, FollowUpNote models
│   ├── services.py                           # Collision-resistant reference ID, proxy-safe rate-limiting
│   ├── validators.py                         # Strict ASCII mobile (0-9) & full name validators
│   ├── urls.py                               # Public routes ('', 'inquiry/success/')
│   ├── views.py                              # home_view and inquiry_success_view
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py                    # Model constraints, WhatsApp URL, string representation
│       ├── test_forms.py                     # Form validations, honeypot, overlong text, mobile checks
│       ├── test_public_views.py              # Public page rendering, PRG submission, XSS prevention
│       ├── test_mobile_validation.py         # ASCII-only enforcement (Devanagari numeral rejection)
│       ├── test_database_config.py           # Multi-database URL parser verification
│       ├── test_proxy_rate_limit.py          # Reverse proxy IP extraction and fail-open rate limiting
│       └── test_setup_admin.py               # Idempotent superuser initialization verification
├── dashboard/
│   ├── migrations/
│   │   └── __init__.py
│   ├── templatetags/
│   │   ├── __init__.py
│   │   └── dashboard_tags.py                 # Query string transform tag for preserving filters in pagination
│   ├── __init__.py
│   ├── admin.py                              # Dashboard admin configuration
│   ├── apps.py                               # App configuration
│   ├── forms.py                              # StaffLoginForm, LeadStatusUpdateForm, LeadForm
│   ├── services.py                           # Metric aggregation, state transitions, CSV sanitization, auth lockout
│   ├── urls.py                               # Protected admin routes (overview, leads, detail, kanban, follow-ups, etc.)
│   ├── views.py                              # staff_required views, brute-force protection, note preservation
│   └── tests/
│       ├── __init__.py
│       ├── test_auth.py                      # Anonymous redirection, staff permissions, safe logout
│       ├── test_leads.py                     # Search, filter, pagination, atomic status transitions
│       ├── test_security.py                  # CSRF enforcement, SQL injection immunity, output escaping
│       ├── test_tabler_features.py           # Kanban, follow-ups, lead create/edit, CSV export, profile
│       ├── test_login_security.py            # Login brute-force lockout & credential protection
│       ├── test_csv_security.py              # CSV formula injection protection
│       ├── test_follow_up_logic.py           # Asia/Kolkata timezone & follow-up mutual exclusivity
│       ├── test_status_transitions.py        # Centralized state machine & form bypass prevention
│       └── test_notes_preservation.py        # FollowUpNote model & 2000-char truncation prevention
├── templates/
│   ├── base.html                             # Base template for public portal with semantic landmarks
│   ├── adminlte_base.html                    # AdminLTE 4 staff dashboard master layout
│   ├── includes/
│   │   ├── messages.html                     # Public dismissible Bootstrap alert banners
│   │   ├── public_navbar.html                # Responsive public header with smooth navigation
│   │   ├── adminlte_sidebar.html             # AdminLTE sidebar navigation with active highlights
│   │   ├── adminlte_header.html              # AdminLTE top bar with user menu & search
│   │   └── adminlte_messages.html            # AdminLTE dismissible alert banners
│   ├── public/
│   │   ├── home.html                         # Public landing page, 4 services, disclaimer, inquiry form
│   │   └── inquiry_success.html              # Reference ID confirmation with copy-to-clipboard button
│   └── dashboard/
│       ├── login.html                        # Admin Login page with brute-force lockout handling
│       ├── overview.html                     # Main Dashboard (8 KPIs + 2 ApexCharts + Recent Leads)
│       ├── leads.html                        # All Inquiries / Leads (Filters, pagination, CSV)
│       ├── lead_detail.html                  # Lead Details (Datagrid, WhatsApp, status update, timeline, notes)
│       ├── lead_form.html                    # Add / Edit Lead Form
│       ├── kanban.html                       # Lead Pipeline / 6-Stage Kanban Board
│       ├── follow_ups.html                   # Follow-up Management Desk (Overdue, Due Today, Upcoming)
│       ├── status_history.html               # Lead Status History Full Audit Trail
│       ├── advanced_search.html              # Search & Advanced Query Builder
│       └── profile.html                      # Admin Profile, Password Change & System Settings
├── static/
│   ├── adminlte/                             # Vendored AdminLTE 4 assets & icons
│   ├── css/
│   │   ├── style.css                         # Scoped public portal styles in Startup Sahay navy
│   │   └── adminlte_custom.css               # AdminLTE enhancements in Startup Sahay corporate brand colors
│   ├── js/
│   │   ├── main.js                           # Vanilla JS: input masking, service selector, clipboard copy
│   │   ├── adminlte_init.js                  # Vanilla JS: AdminLTE initialization
│   │   └── apexcharts.min.js                 # Interactive charts engine
│   └── images/                               # Brand logos and documentation screenshots
└── docs/
    ├── SECURITY_REVIEW.md                    # In-depth security analysis and threat review
    └── AI_CHAT_HISTORY.md                    # Authentic AI development history & disclosures
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

### 3.3 Model: `FollowUpNote` (Table: `inquiries_followupnote`)

| Column Name | Type | Constraints / Attributes | Description |
| :--- | :--- | :--- | :--- |
| `id` | BigAutoField | Primary Key | Note primary key. |
| `inquiry_id` | ForeignKey | `on_delete=CASCADE` | Associated inquiry. Purged if inquiry is removed. |
| `content` | TextField(2000) | Required, Max Length 2000 | Distinct follow-up consultation note content. |
| `created_by_id` | ForeignKey | `on_delete=SET_NULL`, Nullable | Staff author who recorded the follow-up note. Preserved if staff user is deleted. |
| `created_at` | DateTimeField | Auto-now-add, Indexed | Exact timestamp when note was added. |

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
   * **Proxy-Safe Rate Limiting:** Public inquiry submissions throttled by client IP with robust `ipaddress` syntax validation over `X-Forwarded-For` when `USE_X_FORWARDED_FOR=True`, Redis support, and graceful fail-open safety.
3. **Login Brute-Force & Lockout Protection:**
   * IP and username failure tracking in cache.
   * Enforces temporary 5-minute lockout after 5 consecutive failed attempts.
   * Generic lockout error does not reveal whether accounts exist.
   * Resets failure counters immediately upon successful authentication.
4. **CSV Formula Injection (CSV Injection) Protection:**
   * Prepends a single quote `'` to cells whose stripped content starts with dangerous formula trigger characters (`=`, `+`, `-`, `@`, `\t`, `\r`, `|`, `%`).
   * Ensures spreadsheet applications (Excel, LibreOffice, Google Sheets) interpret values as literal text rather than executable formulas.
5. **Cross-Site Request Forgery (CSRF):**
   * `CsrfViewMiddleware` active globally.
   * `{% csrf_token %}` included in every state-changing form.
   * Logout, status updates, and Kanban moves strictly enforce `POST` (rejecting `GET` with HTTP 405).
   * Wildcard testing origins removed; explicitly configured via `CSRF_TRUSTED_ORIGINS`.
6. **Cross-Site Scripting (XSS):**
   * Template autoescaping active; customer message rendered as plain text.
   * Vanilla JS uses `textContent` exclusively (no `innerHTML`).
7. **SQL Injection (SQLi):**
   * 100% ORM parameterized queries (`Q` objects); zero raw SQL.
8. **Session & Cookie Hardening:**
   * `SESSION_COOKIE_HTTPONLY = True`
   * `CSRF_COOKIE_HTTPONLY = True`
   * `SESSION_COOKIE_SAMESITE = 'Lax'`
   * `CSRF_COOKIE_SAMESITE = 'Lax'`
   * Production mode enables `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_SSL_REDIRECT`, `SECURE_HSTS_SECONDS=31536000`, and `SECURE_HSTS_PRELOAD`.

---

## 8. Automated Testing Evidence (102 Tests Passing)

```text
Ran 102 tests in 4.141s
OK (102 passed, 0 failures, 0 errors, 0 skips)
System check identified no issues (0 silenced).
```

### Breakdown of Unit & Integration Test Suites
* **`inquiries/tests/test_models.py` (7 tests):** Model constraints, WhatsApp URL, string representations, cascades.
* **`inquiries/tests/test_forms.py` (10 tests):** Form validations, honeypot rejection, overlong text, mobile checks.
* **`inquiries/tests/test_public_views.py` (8 tests):** Public page rendering, PRG submission, XSS prevention.
* **`inquiries/tests/test_mobile_validation.py` (8 tests):** Strict ASCII digits `0-9` enforcement, Devanagari numerals (`०-९`) rejection, Arabic-Indic numerals rejection, fullwidth digit rejection.
* **`inquiries/tests/test_database_config.py` (3 tests):** Dynamic database URL parsing for PostgreSQL, SQLite, and default fallback.
* **`inquiries/tests/test_proxy_rate_limit.py` (6 tests):** Reverse proxy IP extraction, spoofing protection, fail-open cache safety.
* **`inquiries/tests/test_setup_admin.py` (3 tests):** Idempotent superuser setup, password preservation on redeployment, elimination of hardcoded defaults.
* **`dashboard/tests/test_auth.py` (10 tests):** Anonymous redirection, staff permissions, safe logout, no public registration.
* **`dashboard/tests/test_leads.py` (10 tests):** Search, filter, pagination, atomic status transitions, ordering.
* **`dashboard/tests/test_security.py` (6 tests):** CSRF enforcement, SQL injection immunity, output escaping, cookie settings.
* **`dashboard/tests/test_tabler_features.py` (12 tests):** Kanban, follow-ups, lead create/edit, CSV export, profile settings.
* **`dashboard/tests/test_login_security.py` (4 tests):** Brute-force lockout after 5 failures, credential protection, counter reset on success, non-enumeration.
* **`dashboard/tests/test_csv_security.py` (2 tests):** CSV formula injection protection, sanitization of malicious prefixes, readability preservation.
* **`dashboard/tests/test_follow_up_logic.py` (4 tests):** Asia/Kolkata timezone midnight calculation, Overdue (< today) vs Due Today (today) mutual exclusivity, boundary conditions.
* **`dashboard/tests/test_status_transitions.py` (6 tests):** State machine enforcement, rejection of invalid jumps, form bypass prevention, audit history recording.
* **`dashboard/tests/test_notes_preservation.py` (3 tests):** FollowUpNote model records, data loss prevention, character limit validation without truncation.
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

---

## 11. Authentic Startup Sahay Brand Identity System

In response to technical code review feedback, the complete frontend visual identity was audited against the live official company portal [https://startupsahay.com/](https://startupsahay.com/):

### 11.1 Brand Tokens Extracted & Implemented
* **Primary Brand Colour:** `#FFBA00` (Warm Golden Amber / Brand Gold extracted from live stylesheets and official logo)
* **Contrast Charcoal / Dark Slate:** `#111111` (Official Pitch Black for typography and branding mark) & `#0F172A` (Midnight Slate for sidebar surfaces)
* **Secondary Action Accent:** `#F4511E` (Warm Coral / Vermilion from official active navigation links)
* **Typography:** `'Montserrat', sans-serif` & `'Poppins', sans-serif` (Loaded via Google Fonts, replacing generic system fonts)
* **Official Logo Asset:** `static/images/startupsahay_logo.webp` (dimensions: 988x314, directly extracted from `startupsahay.com/uploads/new_image/cropped-Sahay-r-mark-logo.webp`)
* **Interactive Elements:**
  * Primary Buttons: `#FFBA00` with high-contrast `#111111` bold text and smooth hover elevation.
  * Form Controls: 8px border-radius with `#FFBA00` golden focus ring (`box-shadow: 0 0 0 3px rgba(255, 186, 0, 0.25)`).
  * Login Authentication: Branded card with official logo, subtitle, and interactive show/hide password toggle.
  * ApexCharts: Data series updated to `#FFBA00` brand gold.
  * Maturity Badges: 100px rounded pills with stage-specific high-contrast accessible palettes.
