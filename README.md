# Start-Up Sahay Private Limited — Service Inquiry & Lead Maturity Portal

> **Full-Stack Developer Technical Assignment**  
> Built for: **Start-Up Sahay Private Limited**  
> Technology: Django 5.2 | SQLite | Bootstrap 5 | Vanilla JavaScript  

---

## 1. Project Overview & Objective

This repository contains the production-ready implementation of the **Service Inquiry & Lead Maturity Portal** for **Start-Up Sahay Private Limited**.

The portal serves two distinct user groups:
1. **Public Customer Portal**: Prospective clients explore corporate advisory services, understand statutory boundaries, and submit structured inquiries protected by server-side validation and anti-bot measures.
2. **Restricted Admin Portal**: Authorized staff sign in, monitor pipeline metrics across six maturity stages, inspect customer inquiries, communicate directly via WhatsApp, and advance lead status with complete audit history tracking.

---

## 2. Key Features

* **Public Portal**:
  * Professional, mobile-first responsive design using corporate blue and warm accent palettes.
  * Dedicated service cards for all four core tracks:
    1. *Company Incorporation*
    2. *Startup India DPIIT Recognition*
    3. *Trademark Registration*
    4. *Seed Fund Support*
  * Prominent statutory disclaimers highlighting the company's independent advisory status and non-government affiliation.
  * Authoritative server-side validation for customer name, email, and 10-digit Indian mobile numbers.
  * Anti-bot honeypot field and IP-based rate limiting.
  * Non-guessable, collision-resistant reference IDs (e.g. `SS-20261116-A8F2`).
  * Post/Redirect/Get flow with one-click copy of reference ID.
* **Staff Dashboard**:
  * Role-based access control requiring active staff permissions (`@staff_required`).
  * Dynamic pipeline aggregation cards: Total Inquiries, New, Contacted, Follow-up, Proposal Sent, Mature, Closed.
  * Leads directory ordered newest-first with search (name, mobile, reference ID) and stage filtering.
  * Query-string-preserving pagination.
  * Lead profile view with complete audit trail timeline (previous status, new status, acting admin, remarks, timestamp).
  * Direct WhatsApp engagement link (`wa.me/91...`) with prefilled, URL-encoded template.
  * Atomic status transition engine with row-level locking (`select_for_update`) and no-op transition prevention.

---

## 3. Technology Stack

* **Backend**: Python 3.12, Django 5.2.5
* **Database**: SQLite (configured with relational constraints and indexes; PostgreSQL-ready)
* **Frontend**: HTML5, CSS3 (scoped classes, no destructive overrides), Vanilla JavaScript, Bootstrap 5.3, Bootstrap Icons 1.11
* **Authentication**: Django built-in auth framework with PBKDF2 password hashing
* **Configuration**: Hybrid environment loader (`config/env.py`) supporting `python-dotenv` and standard library `.env` parsing

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
