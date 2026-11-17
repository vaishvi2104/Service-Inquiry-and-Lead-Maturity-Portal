# Sahay LeadFlow Portal

[![Django](https://img.shields.io/badge/Django-5.2-0C4B33?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![UI Framework](https://img.shields.io/badge/UI-AdminLTE_4_Enterprise-184c78?logo=bootstrap&logoColor=white)](https://adminlte.io/)
[![Database](https://img.shields.io/badge/Database-PostgreSQL_%7C_SQLite-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Security Hardened](https://img.shields.io/badge/Security-OWASP_Hardened-success)](docs/SECURITY_REVIEW.md)

A secure, enterprise-grade Service Inquiry & Lead Maturity Portal developed for **Start-Up Sahay Private Limited**, an independent corporate consultancy firm headquartered in Ahmedabad, Gujarat.

The system provides a decoupled architecture featuring a public customer inquiry portal and an internal staff CRM dashboard built on the enterprise **AdminLTE 4** framework, meticulously branded to match the corporate identity of Start-Up Sahay.

---

## 1. Project Overview

**Sahay LeadFlow Portal** is an end-to-end web application that bridges prospective entrepreneurs and corporate legal/business advisors. The platform streamlines statutory service inquiries through structured requirement collection, automated cryptographic reference ID generation, and an administrative lead maturity pipeline tracking prospective clients from initial intake through final conversion.

### Business Domain & Statutory Scope
The portal facilitates advisory consultations across four primary commercial domains:
* **Company Incorporation**: Entity structuring, document preparation, and MCA filing support for Private Limited, LLP, and OPC registrations.
* **Startup India DPIIT Recognition**: Eligibility documentation, application alignment, and compliance review under DPIIT frameworks.
* **Trademark Registration**: Brand name search analysis, Nice classification guidance, and filing documentation support.
* **Seed Fund Support**: Pitch readiness review, incubator application alignment, and compliance guidance.

*Statutory Notice*: Start-Up Sahay Private Limited is an independent professional consultancy and service provider with no government affiliation. All official approvals, certificates, and registrations are granted solely by the respective competent authorities.

---

## 2. Key Features

### Public Customer Portal
* **Corporate Landing Page**: Responsive service catalog, process roadmap, company information, and statutory disclaimers.
* **Structured Inquiry Submission**: Validated customer intake capturing legal name, 10-digit mobile number, business email, service choice, and optional query message.
* **ASCII Mobile Number Validation**: Strict regex rejection of Devanagari numerals (`०-९`), letters, spaces, and punctuation; only ASCII digits `0-9` are accepted.
* **Cryptographic Reference ID**: Generates a non-sequential, collision-resistant reference identifier (`SS-YYYYMMDD-XXXX`) displayed on submission confirmation.
* **Anti-Bot Honeypot**: Hidden `website_url` field that silently rejects automated bot submissions without writing to the database.
* **Proxy-Safe Rate Limiting**: Shared-cache-backed IP throttling that safely validates `X-Forwarded-For` headers behind reverse proxies without trusting spoofed values.
* **Post/Redirect/Get (PRG) Pattern**: Guarantees that refreshing the browser after submission will not generate duplicate database records.

### Staff CRM Portal (AdminLTE 4)
* **Executive Overview**: Dynamic KPI cards computing total inquiries, stage distribution, follow-ups due, and conversion rates, coupled with interactive ApexCharts.
* **Leads Directory**: Paginated, sortable directory supporting real-time text search (name, phone, email, reference ID), stage filter, service filter, and date ranges.
* **Lead Profile & Detail View**: Datagrid of customer information, safely autoescaped query message, internal notes, dedicated follow-up note history, one-click WhatsApp outreach, status update form, and audit timeline.
* **6-Stage Visual Kanban Board**: Interactive board with column counters and quick stage transition triggers (`New Inquiry`, `Contacted`, `Follow-up`, `Proposal Sent`, `Mature`, `Closed`).
* **Follow-up Desk**: Grouped queues with timezone-accurate Indian Standard Time (Asia/Kolkata) boundaries partitioning Overdue (`< start_of_today`), Due Today (`today`), Upcoming (`tomorrow+`), and Unscheduled leads.
* **Follow-up Note Preservation**: Dedicated `FollowUpNote` model storing every note with timestamp and author; rejects requests exceeding limits to prevent silent truncation.
* **Status History Audit Trail**: Immutable log table recording previous stage, new stage, acting staff member, timestamp, and transition remarks.
* **CSV Export with Formula Injection Protection**: Exports filtered leads with automatic neutralization of dangerous spreadsheet triggers (`=`, `+`, `-`, `@`, `\t`, `\r`, `|`, `%`).
* **Brute-Force Login Protection**: Temporary lockout after repeated failed attempts by IP and username without revealing account existence; automatically resets counters upon successful authentication.
* **Direct WhatsApp Outreach**: Generates pre-formatted `https://wa.me/91...` URLs pre-filling customer name, reference ID, and requested service.

---

## 3. Technology Stack

* **Backend Framework**: Django 5.2 (Python 3.12)
* **Database**: Dual-engine support: PostgreSQL for production; SQLite for local development
* **UI Framework**: AdminLTE 4 Enterprise CRM Design System (Bootstrap 5.3 + Bootstrap Icons)
* **Styling**: Scoped corporate CSS (`static/css/style.css`, `static/css/adminlte_custom.css`) in authentic Startup Sahay Golden Amber (`#FFBA00`), Dark Charcoal/Midnight Slate (`#111111` / `#0F172A`), and Warm Coral Accent (`#F4511E`) with Montserrat & Poppins Google Fonts
* **Data Visualization**: ApexCharts (donut stage breakdown and service distribution bar charts)
* **Static File Management**: WhiteNoise with compression and caching support
* **Testing Suite**: Django Test Runner with fast MD5 hasher optimization

---

## 4. Application Architecture

```text
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
                         │   • ASCII Mobile Validation                     │   • Lead Detail & Timeline
                         │   • Reference ID Generation                     │   • 6-Stage Kanban Board
                         │   • Honeypot & Rate Limiting                    │   • Follow-up Management Desk
                         │                                                 │   • Brute-Force Protected Auth
                         │                                                 │   • Formula-Safe CSV Export
                         └────────────────────────┬────────────────────────┘
                                                  │
                                                  ▼
                                  ┌───────────────────────────────┐
                                  │    Django Relational ORM      │
                                  │ (select_for_update, Atomic)   │
                                  └───────────────┬───────────────┘
                                                  │
                                                  ▼
                                  ┌───────────────────────────────┐
                                  │      Relational Database      │
                                  │ (PostgreSQL Prod / SQLite Dev)│
                                  └───────────────────────────────┘
```

---

## 5. Actual Project Directory Structure

```text
startupsahay-portal/
├── manage.py                                 # Django CLI management entrypoint
├── requirements.txt                          # Production & local dependencies
├── .env.example                              # Comprehensive environment template
├── .gitignore                                # Git exclusion rules
├── build.sh                                  # Production deployment build script
├── README.md                                 # Canonical project documentation
├── PROJECT_MASTER_REFERENCE.md               # Architecture & specification reference
├── FINAL_ASSIGNMENT_AUDIT_REPORT.md          # Acceptance audit report
├── config/                                   # Core project configuration
│   ├── env.py                                # Robust environment variable parser
│   ├── settings.py                           # Production-hardened settings
│   ├── urls.py                               # Root URL routing dispatcher
│   ├── wsgi.py                               # WSGI deployment entrypoint
│   └── asgi.py                               # ASGI deployment entrypoint
├── inquiries/                                # Public inquiry portal & core models
│   ├── admin.py                              # Django admin configuration & inlines
│   ├── apps.py                               # Inquiries application config
│   ├── forms.py                              # Inquiry submission form with honeypot
│   ├── models.py                             # Inquiry, LeadStatusHistory, FollowUpNote
│   ├── services.py                           # Ref ID generator, proxy-safe rate limiting
│   ├── validators.py                         # Strict ASCII mobile & full name validators
│   ├── views.py                              # Public landing & PRG confirmation views
│   ├── migrations/                           # Relational schema migrations
│   └── tests/                                # Public portal, model, and form test suites
├── dashboard/                                # Staff administrative CRM
│   ├── admin.py                              # Dashboard admin configuration
│   ├── apps.py                               # Dashboard application config
│   ├── forms.py                              # Login, status transition, lead edit forms
│   ├── services.py                           # Dynamic metrics, transitions, CSV sanitizer
│   ├── urls.py                               # Dashboard URL routes
│   ├── views.py                              # 10 AdminLTE CRM views with brute-force guards
│   ├── templatetags/                         # Query-string pagination helper tags
│   └── tests/                                # Auth, leads, security, and feature tests
├── templates/
│   ├── base.html                             # Public website master layout
│   ├── adminlte_base.html                    # AdminLTE 4 staff dashboard master layout
│   ├── public/                               # Public landing & confirmation templates
│   │   ├── home.html
│   │   └── inquiry_success.html
│   ├── dashboard/                            # 10 Staff CRM view templates
│   │   ├── login.html
│   │   ├── overview.html
│   │   ├── leads.html
│   │   ├── lead_detail.html
│   │   ├── lead_form.html
│   │   ├── kanban.html
│   │   ├── follow_ups.html
│   │   ├── status_history.html
│   │   ├── advanced_search.html
│   │   └── profile.html
│   └── includes/                             # Partials: header, sidebar, navbar, messages
│       ├── adminlte_header.html
│       ├── adminlte_sidebar.html
│       ├── adminlte_messages.html
│       ├── public_navbar.html
│       └── messages.html
├── static/
│   ├── adminlte/                             # Vendored AdminLTE 4 assets & icons
│   ├── css/                                  # Public style.css & adminlte_custom.css
│   ├── js/                                   # main.js, adminlte_init.js, apexcharts.min.js
│   └── images/                               # Brand logos & documentation screenshots
└── docs/
    ├── SECURITY_REVIEW.md                    # Threat model & vulnerability mitigations
    └── AI_CHAT_HISTORY.md                    # Development trajectory & disclosure
```

---

## 6. Database Models

The relational schema consists of three core models:

### 1. `Inquiry` Model
* `reference_id`: Cryptographic uppercase identifier (`SS-YYYYMMDD-XXXX`), unique, indexed.
* `full_name`: Customer full legal/business contact name (max 120 chars, control characters stripped).
* `mobile_number`: 10-digit Indian mobile number, indexed, strictly ASCII digits `0-9`.
* `email`: Primary email address, indexed.
* `service`: Selected consultancy service track (Choices: `company_incorporation`, `dpiit_recognition`, `trademark_registration`, `seed_fund_support`).
* `status`: Maturity stage (Choices: `new`, `contacted`, `follow_up`, `proposal_sent`, `mature`, `closed`).
* `follow_up_date`: Timezone-aware scheduled follow-up date and time (`Asia/Kolkata`).
* `assigned_to`: ForeignKey to staff `User` (`SET_NULL`, nullable).
* `internal_notes`: Staff consultation notes (max 2000 chars, protected against silent truncation).
* `message`: Customer's original inquiry message (max 2000 chars, safely escaped).
* `created_at` / `updated_at`: Auto-managed timestamps.

### 2. `LeadStatusHistory` Model (Audit Trail)
* `inquiry`: ForeignKey to `Inquiry` (`CASCADE`).
* `previous_status`: Previous pipeline stage.
* `new_status`: New pipeline stage.
* `updated_by`: ForeignKey to `User` (`SET_NULL`, preserves record if staff account is deleted).
* `remarks`: Transition remarks or consultation notes (max 500 chars).
* `created_at`: Exact timestamp of transition.

### 3. `FollowUpNote` Model (Historical Record Preservation)
* `inquiry`: ForeignKey to `Inquiry` (`CASCADE`).
* `content`: Discrete note content (max 2000 chars).
* `created_by`: Staff member who authored the note (`SET_NULL`).
* `created_at`: Timestamp of note creation.

---

## 7. Security Hardening Summary

| Security Control | Implementation Mechanism | Location |
| :--- | :--- | :--- |
| **No Hardcoded Credentials** | All admin credentials read from environment; existing passwords preserved during build | `inquiries/management/commands/setup_admin.py` |
| **Production Settings** | `DEBUG=False` by default; explicit `ALLOWED_HOSTS`; HTTPS redirect; HSTS preload; secure cookies | `config/settings.py` |
| **Clean CSRF Origins** | Wildcards removed; origins read strictly from `CSRF_TRUSTED_ORIGINS` env var | `config/settings.py` |
| **Proxy-Safe Rate Limiting** | Validates `X-Forwarded-For` with `ipaddress` syntax; Redis support; fail-open safety | `inquiries/services.py` |
| **Login Brute-Force Lockout** | IP and username failure tracking; 5-attempt threshold; 5-min temporary lockout; resets on success | `dashboard/views.py` |
| **CSV Formula Injection** | Prepends single quote `'` to dangerous prefixes (`=`, `+`, `-`, `@`, `\t`, `\r`, `\|`, `%`) | `dashboard/services.py` |
| **ASCII Mobile Validation** | Explicit `^[0-9]{10}$` regex with `re.ASCII` rejecting Devanagari numerals | `inquiries/validators.py` |
| **Status Transition Locking** | State machine validation; row locking via `select_for_update()`; atomic audit logging | `dashboard/services.py` |
| **Follow-up Note Preservation** | Dedicated `FollowUpNote` model; explicit error on limit exceeded; zero silent truncation | `dashboard/views.py` |
| **Open Redirect Defense** | Validates `next` parameter via `url_has_allowed_host_and_scheme` | `dashboard/views.py` |

---

## 8. Installation & Local Development Setup

### 1. Prerequisites
* Python 3.10, 3.11, or 3.12
* Git

### 2. Clone Repository & Setup Virtual Environment
```bash
# 1. Clone repository
git clone https://github.com/vaishvi2104/Service-Inquiry-and-Lead-Maturity-Portal.git
cd Service-Inquiry-and-Lead-Maturity-Portal/startupsahay-portal

# 2. Create virtual environment
# Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS:
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy the template to create `.env`:
```bash
# Windows (PowerShell):
Copy-Item .env.example .env

# Linux / macOS:
cp .env.example .env
```
For local development, the default `.env` works out-of-the-box using local SQLite.

### 4. Apply Database Migrations
```bash
python manage.py migrate
```

### 5. Create Administrative Superuser
Option A: Secure interactive prompt:
```bash
python manage.py createsuperuser
```
Option B: Automated setup from `.env` variables (`ADMIN_USERNAME`, `ADMIN_PASSWORD`):
```bash
python manage.py setup_admin
```

### 6. Run Development Server
```bash
python manage.py runserver
```
Access the portal:
* **Public Customer Website**: `http://127.0.0.1:8000/`
* **Staff CRM Dashboard**: `http://127.0.0.1:8000/dashboard/`
* **Django Admin**: `http://127.0.0.1:8000/admin/`

---

## 9. Production Deployment Guide

### Database Configuration (PostgreSQL)
Set the `DATABASE_URL` environment variable:
```bash
DATABASE_URL=postgresql://db_user:db_password@db_host:5432/startupsahay_db
```
The application dynamically configures PostgreSQL using `django.db.backends.postgresql` and `psycopg2-binary`.

### Production Security Flags
Configure the following in production:
```dotenv
DEBUG=False
SECRET_KEY=generate-a-strong-random-50-character-string
ALLOWED_HOSTS=portal.startupsahay.com,crm.startupsahay.com
CSRF_TRUSTED_ORIGINS=https://portal.startupsahay.com,https://crm.startupsahay.com
USE_X_FORWARDED_FOR=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
```

### Shared Cache (Redis)
For multi-worker deployments (e.g., Gunicorn with multiple worker processes), configure Redis:
```dotenv
REDIS_URL=redis://127.0.0.1:6379/1
```

### Build Script (`build.sh`)
For platforms like Render, Railway, AWS, or Docker:
```bash
chmod +x build.sh
./build.sh
```

---

## 10. Running Automated Tests

Execute the automated test suite with verbose output:
```bash
python manage.py test -v 2
```

To run individual test modules:
```bash
# Model tests
python manage.py test inquiries.tests.test_models

# Form validation & honeypot tests
python manage.py test inquiries.tests.test_forms

# Public portal & submission tests
python manage.py test inquiries.tests.test_public_views

# Staff authentication & brute-force tests
python manage.py test dashboard.tests.test_auth

# Leads workflow & search tests
python manage.py test dashboard.tests.test_leads

# Security & formula injection tests
python manage.py test dashboard.tests.test_security

# Follow-up desk, Kanban, and note preservation tests
python manage.py test dashboard.tests.test_tabler_features
```
