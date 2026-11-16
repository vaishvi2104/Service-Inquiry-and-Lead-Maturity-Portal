# Start-Up Sahay Private Limited — Sahay LeadFlow Portal

> **Full-Stack Developer Technical Assignment & Admin Design System**  
> Built for: **Start-Up Sahay Private Limited**  
> Admin Design Framework: **Official Tabler UI (`@tabler/core` + Tabler Icons + ApexCharts)**  
> Backend: Django 5.2 | SQLite | Python 3.12 | Vanilla JavaScript  

---

## 1. Project Overview & Objective

This repository contains the complete, production-ready implementation of the **Sahay LeadFlow** Service Inquiry & Lead Maturity Portal for **Start-Up Sahay Private Limited**.

The portal consists of:
1. **Public Customer Portal**: Prospective clients explore corporate advisory services (Company Incorporation, Startup India DPIIT Recognition, Trademark Registration, Seed Fund Support), review mandatory statutory disclaimers, and submit structured inquiries protected by server-side validation and anti-bot measures.
2. **Tabler Admin Management Portal**: Authorized staff sign in to a fully integrated **Tabler UI** dashboard featuring 10 dedicated management pages, dynamic KPI cards, interactive ApexCharts analytics, a visual 6-stage Kanban board, follow-up desk, lead creation/editing, audit history log, multi-criteria search, CSV export, and profile settings with Light/Dark mode.

---

## 2. Tabler Admin Interface Pages

1. **Admin Login** (`/dashboard/login/`): Tabler single-card layout with brand treatment and error handling.
2. **Main Dashboard** (`/dashboard/`): 8 KPI metric cards (Total Inquiries, New, Contacted, Follow-ups Due, Proposals Sent, Mature, Closed, Conversion Rate) + ApexCharts for stage distribution and service statistics + recent inquiries table + follow-up desk widget.
3. **All Inquiries / Leads** (`/dashboard/leads/`): Tabler striped table with search, stage filter, service filter, date range filter, pagination, quick actions, and CSV export.
4. **Lead Details** (`/dashboard/leads/<ref>/`): Full customer profile, datagrid, prefilled WhatsApp outreach link (`wa.me/91...`), stage transition form, follow-up scheduling, and stage transition audit timeline.
5. **Add / Edit Lead** (`/dashboard/leads/create/` & `.../edit/`): Full form for manually registering new inquiries and editing existing leads.
6. **Lead Pipeline / Kanban** (`/dashboard/kanban/`): Visual 6-stage Kanban board with column counts and 1-click stage transition action menus.
7. **Follow-up Desk** (`/dashboard/follow-ups/`): Dedicated follow-up management categorizing Overdue, Due Today, and Upcoming follow-ups.
8. **Lead Status History** (`/dashboard/history/`): Full organizational audit trail table tracking all transitions across all leads.
9. **Search & Advanced Filters** (`/dashboard/search/`): Multi-criteria query builder with date ranges, service/stage filters, and CSV export.
10. **Admin Profile & Settings** (`/dashboard/profile/`): Staff credentials, profile update form, password change form, and system parameters.

---

## 3. Technology Stack & Licensing

* **Backend**: Python 3.12, Django 5.2.5
* **Database**: SQLite (relational schema with constraints and row-level locking)
* **Admin Design System**: Official Tabler UI (`@tabler/core@1.6.1`, MIT License)
* **Icons**: Tabler Icons Webfont (`@tabler/icons-webfont@3.51.0`, MIT License)
* **Charts**: ApexCharts (`apexcharts@3.54.1`, MIT License)
* **Public Website**: Dedicated custom CSS (`static/css/style.css`) and Vanilla JavaScript (zero framework dependencies)
* **Licenses**: Permissive MIT licenses across all bundled libraries; documented in `static/tabler/LICENSE.md`.

---

## 4. Directory Layout

```text
startupsahay-portal/
├── manage.py                                 # Django CLI runner
├── requirements.txt                          # Python dependencies
├── .env.example                              # Environment configuration template
├── README.md                                 # Project documentation
├── PROJECT_MASTER_REFERENCE.md               # Master reference manual
├── FINAL_ASSIGNMENT_AUDIT_REPORT.md          # Acceptance audit report
├── config/                                   # Project configuration and settings
├── inquiries/                                # Public portal and core data models
│   ├── forms.py                              # Inquiry submission form
│   ├── models.py                             # Inquiry & LeadStatusHistory models
│   ├── services.py                           # Reference ID generator & persistence
│   ├── validators.py                         # Strict name & 10-digit mobile validators
│   └── tests/                                # App unit & integration tests
├── dashboard/                                # Staff lead management portal
│   ├── forms.py                              # Staff login & status update forms
│   ├── services.py                           # Metrics aggregation & atomic transition
│   ├── templatetags/                         # Query string preservation helper
│   └── tests/                                # Auth, leads, & security tests
├── templates/                                # Django templates
├── static/                                   # CSS and Vanilla JavaScript
└── docs/
    ├── SECURITY_REVIEW.md                    # Threat analysis & security controls
    └── AI_CHAT_HISTORY.md                    # Authentic AI development log
```

---

## 5. Getting Started (Local Setup)

### Prerequisites
* Python 3.10+ (Tested on Python 3.12.6)
* Git (Optional, for version control)

### Windows PowerShell Setup

```powershell
# 1. Clone or navigate to the project directory
cd "C:\Users\VAISHVI SHAH\.gemini\antigravity\scratch\startupsahay-portal"

# 2. Create and activate a virtual environment (optional but recommended)
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure local environment variables
Copy-Item .env.example .env

# 5. Run database migrations
python manage.py migrate

# 6. Create an administrator / staff account
python manage.py createsuperuser

# 7. Run the test suite
python manage.py test -v 2

# 8. Start the development server
python manage.py runserver
```

### macOS / Linux Setup

```bash
# 1. Navigate to directory
cd startupsahay-portal

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure local environment variables
cp .env.example .env

# 5. Run database migrations
python3 manage.py migrate

# 6. Create an administrator account
python3 manage.py createsuperuser

# 7. Run the test suite
python3 manage.py test -v 2

# 8. Start the development server
python3 manage.py runserver
```

Access the application in your browser:
* **Public Customer Portal**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
* **Staff Admin Portal**: [http://127.0.0.1:8000/dashboard/](http://127.0.0.1:8000/dashboard/)
* **Django Admin**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 6. Verification & Automated Test Results

The automated test suite contains **51 tests** verifying models, forms, public views, staff authentication, leads management, and security controls:

```text
Creating test database for alias 'default'...
Ran 51 tests in 23.698s

OK (0 failures, 0 errors, 0 skips)
System check identified no issues (0 silenced).
```

To run individual test modules:
```powershell
python manage.py test inquiries.tests.test_models
python manage.py test inquiries.tests.test_forms
python manage.py test inquiries.tests.test_public_views
python manage.py test dashboard.tests.test_auth
python manage.py test dashboard.tests.test_leads
python manage.py test dashboard.tests.test_security
```

---

## 7. Security Architecture Summary

* **CSRF Enforcement**: Active across all endpoints; state changes (`logout`, `status_update`) strictly reject `GET` requests (405).
* **Anti-Bot & Abuse**: Invisible honeypot traps form bots; IP-based rate limiting restricts excessive submissions.
* **XSS Prevention**: Django template autoescaping active; vanilla JavaScript strictly uses `textContent`.
* **SQL Injection Immunity**: Pure ORM parameterized queries; no raw SQL strings.
* **Hardened Cookies**: `SESSION_COOKIE_HTTPONLY=True`, `CSRF_COOKIE_HTTPONLY=True`, `SameSite='Lax'`.
* **Atomic Lead Transitions**: Database transactions with `select_for_update` row locking prevent race conditions.
* See [docs/SECURITY_REVIEW.md](docs/SECURITY_REVIEW.md) for full threat matrix.

---

## 8. Authentic AI Development History

In compliance with the assignment instructions, this project was built using the **Google Antigravity IDE** powered by **Gemini 3.8 Flash High**.

* Complete development narrative: [docs/AI_CHAT_HISTORY.md](docs/AI_CHAT_HISTORY.md)
* Raw machine trajectory transcript:
  `C:\Users\VAISHVI SHAH\.gemini\antigravity\brain\73b26742-8e19-44e8-90c1-aa58fee1e77d\.system_generated\logs\transcript.jsonl`
* Conversation ID: `73b26742-8e19-44e8-90c1-aa58fee1e77d`

---

## 9. Contact & Company Details

* **Company**: **Start-Up Sahay Private Limited**
* **Address**: B-304, Ganesh Glory 11, Jagatpur Road, Gota, Ahmedabad, Gujarat 382470
* **Email**: info@startupsahay.com
* **Phone**: +91-63526-75546
* **Website**: [https://www.startupsahay.com/](https://www.startupsahay.com/)
