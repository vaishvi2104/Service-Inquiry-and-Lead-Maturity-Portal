# Sahay LeadFlow Portal

[![Django](https://img.shields.io/badge/Django-5.2-0C4B33?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Tabler UI](https://img.shields.io/badge/UI-Tabler_Core_1.6.1-0054a6?logo=tabler&logoColor=white)](https://tabler.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](static/tabler/LICENSE.md)
[![Tests](https://img.shields.io/badge/Tests-63%20Passed-success)](#11-running-tests)

A secure, enterprise-grade Service Inquiry & Lead Maturity Portal developed for **Start-Up Sahay Private Limited**, an independent corporate consultancy firm headquartered in Ahmedabad, Gujarat.

The system provides a decoupled architecture featuring a public customer inquiry interface and an administrative CRM dashboard built with the official **Tabler UI** design system.

---

## 1. Project Overview

**Sahay LeadFlow Portal** is an end-to-end web application that bridges prospective entrepreneurs and corporate consultants. The platform streamlines statutory service inquiries through structured requirement collection, automated reference ID generation, and an administrative lead maturity pipeline tracking prospective clients from first contact through formal engagement.

### Business Domain & Statutory Scope
The portal facilitates advisory consultations across four primary commercial domains:
* **Company Incorporation**: Entity structuring, document preparation, and MCA filing support for Private Limited, LLP, and OPC registrations.
* **Startup India DPIIT Recognition**: Eligibility documentation, application alignment, and compliance review under DPIIT frameworks.
* **Trademark Registration**: Brand name search analysis, Nice classification guidance, and filing documentation support.
* **Seed Fund Support**: Pitch readiness review, incubator application alignment, and compliance guidance.

*Statutory Notice*: Start-Up Sahay Private Limited is an independent consultancy firm with no government affiliation. All official approvals, certificates, and registrations are granted solely by the respective competent authorities.

---

## 2. Key Features

### Public Customer Interface
* **Responsive Service Catalog**: Comprehensive service overviews with mandatory statutory disclaimers and advisory scopes.
* **Structured Inquiry Submission**: Validated customer intake capturing name, contact information, service track, and requirements.
* **Cryptographic Reference ID**: Generates a non-sequential, collision-resistant reference identifier (`SS-YYYYMMDD-XXXX`) displayed on submission confirmation.
* **Anti-Bot & Abuse Protections**: Server-enforced honeypot detection and cache-backed IP rate limiting to prevent spam and resource exhaustion.
* **Post/Redirect/Get (PRG) Pattern**: Prevents duplicate submissions on browser refresh.

### Tabler Administrative CRM Dashboard
* **10 Dedicated Management Views**: Executive Overview, Leads Directory, Lead Profile & Details, Add/Edit Lead, 6-Stage Kanban Pipeline, Follow-up Desk, Status History Audit Trail, Advanced Search & Query Builder, Admin Profile, and System Settings.
* **Real-Time KPI Cards**: 8 dynamic metric cards calculating total inquiries, stage counts, follow-ups due, and lead conversion rates.
* **Interactive ApexCharts**: Visual stage distribution donut chart and service track breakdown bar chart powered by real ORM queries.
* **6-Stage Visual Kanban Board**: Interactive board with column counters and quick stage transition actions.
* **Follow-up Desk**: Grouped queues prioritizing Overdue, Due Today, Upcoming, and Unscheduled follow-ups.
* **Audit Trail**: Every stage change atomically records the previous stage, new stage, acting staff member, timestamp, and optional transition remarks.
* **WhatsApp Direct Engagement**: Pre-configured `wa.me` links with encoded message templates and standard Indian mobile formatting (`+91`).
* **Multi-Criteria Search & CSV Export**: Comprehensive query builder supporting text search, stage filtering, service filtering, and date range filtering with CSV export.
* **Dark / Light Theme Engine**: Integrated Tabler theme switcher persisting user preferences via `localStorage`.

---

## 3. Technology Stack

* **Backend Framework**: Django 5.2.5 (Python 3.12)
* **Database**: SQLite (relational schema with row-level locking via `select_for_update()`; PostgreSQL-ready)
* **Admin UI Framework**: Official Tabler UI (`@tabler/core` 1.6.1), Tabler Icons Webfont (`@tabler/icons-webfont` 3.51.0)
* **Data Visualization**: ApexCharts 3.54.1 (MIT License)
* **Public Frontend**: Modular CSS (`static/css/style.css`), Vanilla JavaScript (zero framework runtime overhead)
* **Testing Framework**: Django Test Runner, Playwright Chromium for live browser automation
* **Licensing**: Permissive open-source licenses (MIT) across all bundled third-party assets (documented in `static/tabler/LICENSE.md`)

---

## 4. Application Architecture

```
                                  ┌───────────────────────────────┐
                                  │      Client Web Browser       │
                                  └───────────────┬───────────────┘
                                                  │
                                       HTTP / HTTPS Requests
                                                  │
                                                  ▼
                                  ┌───────────────────────────────┐
                                  │     Django Middleware Layer   │
                                  │   (Security, Session, CSRF)   │
                                  └───────────────┬───────────────┘
                                                  │
                         ┌────────────────────────┴────────────────────────┐
                         │                                                 │
                         ▼                                                 ▼
             ┌───────────────────────┐                         ┌───────────────────────┐
             │    inquiries App      │                         │     dashboard App     │
             │   (Public Portal)     │                         │   (Staff CRM Portal)  │
             └───────────┬───────────┘                         └───────────┬───────────┘
                         │                                                 │
                         │   • Home & Services                             │   • Executive Overview
                         │   • Inquiry Submission                          │   • All Leads Directory
                         │   • Form Validation                             │   • Lead Detail & Timeline
                         │   • Reference ID Generation                     │   • 6-Stage Kanban Board
                         │   • Rate Limiting & Honeypot                    │   • Follow-up Management
                         │                                                 │   • Advanced Search & CSV
                         │                                                 │   • Profile & Dark Mode
                         └────────────────────────┬────────────────────────┘
                                                  │
                                                  ▼
                                  ┌───────────────────────────────┐
                                  │    Django Relational ORM      │
                                  │  (Parameterized Q, Locking)   │
                                  └───────────────┬───────────────┘
                                                  │
                                                  ▼
                                  ┌───────────────────────────────┐
                                  │      Relational Database      │
                                  │   (Inquiry, StatusHistory)    │
                                  └───────────────────────────────┘
```

The system maintains a clean decoupling between the client-facing inquiry portal and the internal staff dashboard:
* **`inquiries` Module**: Handles public routing, rate limiting, anti-bot validation, inquiry persistence, and reference ID generation.
* **`dashboard` Module**: Protected administrative interface providing lead maturity workflows, analytics aggregation, and audit logging.

---

## 5. Project Structure

```text
startupsahay-portal/
├── manage.py                                 # Django CLI entrypoint
├── requirements.txt                          # Production & development dependencies
├── .env.example                              # Safe environment template
├── .gitignore                                # Version control exclusion rules
├── README.md                                 # Main project documentation
├── PROJECT_MASTER_REFERENCE.md               # Master reference manual
├── FINAL_ASSIGNMENT_AUDIT_REPORT.md          # Acceptance audit report
├── TABLER_INTEGRATION_REPORT.md              # Tabler UI design system report
├── config/                                   # Project configuration
│   ├── env.py                                # Hybrid environment loader
│   ├── settings.py                           # Application settings & security controls
│   ├── urls.py                               # Root URL dispatcher
│   ├── wsgi.py                               # WSGI deployment entrypoint
│   └── asgi.py                               # ASGI deployment entrypoint
├── inquiries/                                # Public intake & core data models
│   ├── forms.py                              # Inquiry submission form with honeypot
│   ├── models.py                             # Inquiry & LeadStatusHistory models
│   ├── services.py                           # Reference ID generator & persistence
│   ├── validators.py                         # Strict name & 10-digit mobile validators
│   ├── views.py                              # Public home & confirmation views
│   └── tests/                                # Automated unit & integration tests
├── dashboard/                                # Staff administrative CRM
│   ├── forms.py                              # Staff login, status update, & lead forms
│   ├── services.py                           # Metric aggregation & atomic stage transitions
│   ├── templatetags/                         # Query-string pagination helper
│   ├── views.py                              # 10 Tabler admin dashboard views
│   └── tests/                                # Staff auth, leads, & security tests
├── templates/
│   ├── base.html                             # Base template for public portal
│   ├── tabler_base.html                      # Primary Tabler admin dashboard base layout
│   ├── public/                               # Public landing & confirmation pages
│   ├── dashboard/                            # 10 Tabler admin dashboard templates
│   └── includes/                             # Navigation, headers, and alert partials
├── static/
│   ├── css/                                  # Public styles & dashboard enhancements
│   ├── js/                                   # Vanilla JavaScript utilities
│   └── tabler/                               # Locally hosted Tabler Core & ApexCharts assets
└── docs/
    ├── SECURITY_REVIEW.md                    # In-depth security analysis & threat matrix
    └── AI_CHAT_HISTORY.md                    # Authentic AI-assisted development record
```

---

## 6. Database Design

The relational data model consists of two core entities optimized with indexes for high-speed filtering and search:

### `Inquiry` Entity
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | BigAutoField | Primary Key | Internal identifier. |
| `reference_id` | CharField(24) | Unique, Indexed | Non-sequential reference code (e.g. `SS-20261116-A8F2`). |
| `full_name` | CharField(120) | Required | Validated customer name (control characters stripped). |
| `mobile_number` | CharField(10) | Indexed | Exactly 10 numeric ASCII digits. |
| `email` | EmailField(254)| Indexed | Customer primary email address. |
| `service` | CharField(40) | Choices, Indexed | One of the 4 statutory service choices. |
| `status` | CharField(30) | Choices, Indexed | Current maturity stage (`new`, `contacted`, `follow_up`, `proposal_sent`, `mature`, `closed`). |
| `follow_up_date`| DateTimeField | Nullable, Indexed| Scheduled consultation timestamp. |
| `assigned_to` | ForeignKey | Nullable, SET_NULL | Assigned staff consultant (`auth.User`). |
| `message` | TextField(2000)| Blankable | Customer inquiry description (safely autoescaped). |
| `internal_notes`| TextField | Blankable | Confidential staff internal notes. |
| `created_at` | DateTimeField | Auto-now-add, Indexed | Submission timestamp. |
| `updated_at` | DateTimeField | Auto-now | Timestamp of last modification. |

### `LeadStatusHistory` Entity (Audit Trail)
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | BigAutoField | Primary Key | History record identifier. |
| `inquiry_id` | ForeignKey | CASCADE, Indexed | Target inquiry record. |
| `previous_status`| CharField(30) | Choices | Stage prior to modification. |
| `new_status` | CharField(30) | Choices | Newly applied pipeline stage. |
| `updated_by_id` | ForeignKey | Nullable, SET_NULL | Staff user who authorized the transition. |
| `remarks` | TextField(500) | Blankable | Optional transition notes / client feedback. |
| `created_at` | DateTimeField | Auto-now-add, Indexed | Exact timestamp of stage change. |

---

## 7. Security Implementation

1. **Role-Based Access Control**: All administrative views enforce the custom `@staff_required` decorator. Unauthenticated requests redirect to the login screen with a safe `?next=` parameter; authenticated non-staff users receive HTTP 403 Forbidden.
2. **Open Redirect Mitigation**: Login redirects validate target URLs via `url_has_allowed_host_and_scheme(url=redirect_to, allowed_hosts={request.get_host()})`.
3. **Cross-Site Request Forgery (CSRF)**: Django's `CsrfViewMiddleware` is globally enforced. State mutations (`logout`, `status_update`, `kanban_move`) strictly require POST requests.
4. **SQL Injection Immunity**: 100% of database interactions utilize Django ORM parameterized queries (`Q` objects); zero raw SQL strings are present.
5. **Cross-Site Scripting (XSS) Prevention**: Template autoescaping is preserved across all views. Dynamic DOM updates use vanilla JS `textContent` exclusively.
6. **Anti-Bot & Rate Limiting**: The public form includes a hidden honeypot (`website_url`) that rejects automated scripts without database writes, supplemented by cache-backed IP rate limiting (`check_rate_limit`).
7. **Concurrency Race Condition Prevention**: Stage updates execute inside `transaction.atomic()` with `select_for_update()` row locking. Redundant no-op updates (same status) are rejected.
8. **Cookie & Session Hardening**: `SESSION_COOKIE_HTTPONLY = True`, `CSRF_COOKIE_HTTPONLY = True`, and `SameSite = 'Lax'` are configured by default.

---

## 8. Installation and Setup

### Prerequisites
* Python 3.10 or higher (Tested on Python 3.12)
* Git

### Step-by-Step Installation

```bash
# 1. Clone the repository
git clone https://github.com/vaishvi2104/Service-Inquiry-and-Lead-Maturity-Portal.git
cd Service-Inquiry-and-Lead-Maturity-Portal

# 2. Navigate to project root
cd startupsahay-portal

# 3. Create and activate a virtual environment
# On Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1

# On macOS/Linux:
python3 -m venv venv
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
```

---

## 9. Environment Configuration

Copy the example configuration file to create your local `.env`:

```bash
# On Windows (PowerShell):
Copy-Item .env.example .env

# On macOS/Linux:
cp .env.example .env
```

Key environment variables:
* `SECRET_KEY`: Cryptographic signing key (required in production; safe default used in development).
* `DEBUG`: Set to `True` for local development, `False` for production.
* `ALLOWED_HOSTS`: Comma-separated list of permitted hostnames.
* `INQUIRY_RATE_LIMIT_MAX_REQUESTS`: Maximum allowed submissions per IP window (default: `5`).
* `INQUIRY_RATE_LIMIT_WINDOW_SECONDS`: Rate limiting time window in seconds (default: `600`).

---

## 10. Running the Application

```bash
# 1. Apply database migrations
python manage.py migrate

# 2. Start the development server
python manage.py runserver
```

Once running, access the portal at:
* **Public Customer Website**: `http://127.0.0.1:8000/`
* **Staff Tabler CRM Dashboard**: `http://127.0.0.1:8000/dashboard/`
* **Django Admin**: `http://127.0.0.1:8000/admin/`

---

## 11. Running Tests

The test suite contains **63 automated tests** covering data models, form validations, rate limiting, staff authentication, leads management, atomic transactions, and security protections:

```bash
# Execute the full automated test suite
python manage.py test -v 2
```

```text
Ran 63 tests in 35.758s
OK (63 passed, 0 failures, 0 errors, 0 skips)
System check identified no issues (0 silenced).
```

### Module Test Execution
```bash
# Model tests
python manage.py test inquiries.tests.test_models

# Form validation & honeypot tests
python manage.py test inquiries.tests.test_forms

# Public portal & PRG flow tests
python manage.py test inquiries.tests.test_public_views

# Staff authentication & RBAC tests
python manage.py test dashboard.tests.test_auth

# Leads workflow & filter tests
python manage.py test dashboard.tests.test_leads

# Security & injection immunity tests
python manage.py test dashboard.tests.test_security

# Tabler features (Kanban, Follow-ups, CSV, Profile) tests
python manage.py test dashboard.tests.test_tabler_features
```

---

## 12. Admin Account Setup

To create an administrative user for accessing the Tabler dashboard:

```bash
python manage.py createsuperuser
```

Enter your desired username, official email, and password. Once created, sign in at `http://127.0.0.1:8000/dashboard/login/`.

---

## 13. AI-Assisted Development Disclosure

AI tools were used during development for assistance with implementation, debugging, documentation, and code review.

The development workflow, implementation decisions, and verification results are documented in the accompanying development history.

For full details, see [docs/AI_CHAT_HISTORY.md](docs/AI_CHAT_HISTORY.md).

---

## 14. Future Improvements

* **Login Rate Limiting**: Implement `django-axes` on `/dashboard/login/` for automated account lockout after consecutive failed authentication attempts.
* **CSV Formula Sanitization**: Prepend a single quote `'` to text cells beginning with `=`, `+`, `-`, or `@` to defend against spreadsheet formula injection.
* **Content Security Policy (CSP)**: Integrate `django-csp` with nonce-based script execution to further harden frontend assets.
* **Enterprise Database Migration**: Transition from SQLite to PostgreSQL for multi-region or high-concurrency enterprise deployments.
* **Automated Notification Webhooks**: Integrate transactional email and WhatsApp Business API webhooks for automated status notifications.
