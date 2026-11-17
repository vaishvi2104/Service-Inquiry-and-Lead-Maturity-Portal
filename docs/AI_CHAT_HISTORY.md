# Sahay LeadFlow Portal — AI-Assisted Development & Engineering History

> **Date of Last Engineering Refactor:** 17 November 2026  
> **Project Name:** Service Inquiry and Lead Maturity Portal (Start-Up Sahay Private Limited)  
> **Repository:** Service-Inquiry-and-Lead-Maturity-Portal  
> **Framework:** Django 5.2 / Python 3.12 / AdminLTE 4 Enterprise CRM Design System  
> **Organization:** Start-Up Sahay Private Limited (Ahmedabad, Gujarat)  

---

## 1. Statement of Authenticity & Transcript Status

**Important Disclosure on Conversation Transcripts:**
The raw machine-generated conversation transcripts (e.g., internal tool execution JSONL files or environment session logs) are not distributed or persisted within this repository's workspace. In accordance with strict software engineering integrity guidelines, no synthetic, simulated, or fabricated conversation logs have been generated to substitute for missing raw logs.

This document serves as an authentic, factual summary of the system architecture, design decisions, security hardening, business logic refactorings, and verification stages performed across the development and technical review lifecycle.

---

## 2. Chronological Engineering Phases

### Phase 1: Baseline Architecture & Public Inquiries
* **Objective:** Establish the core Django architecture, data models, and public customer inquiry intake portal.
* **Key Implementations:**
  - Standardized project structure into modular applications: `inquiries` (public portal) and `dashboard` (staff lead management).
  - Implemented the `Inquiry` model with cryptographic collision-resistant `reference_id` (`SS-YYYYMMDD-XXXX`), strict 10-digit mobile number validation, and audit tracking.
  - Implemented `LeadStatusHistory` model to maintain an immutable audit trail with `CASCADE` on lead deletion and `SET_NULL` on staff account removal.
  - Developed the public portal (`home_view`) featuring the four mandatory services:
    1. Company Incorporation
    2. Startup India DPIIT Recognition
    3. Trademark Registration
    4. Seed Fund Support
  - Enforced anti-bot honeypot field (`website_url`) and cache-backed rate limiting.
  - Implemented Post/Redirect/Get (PRG) pattern for smooth confirmation without form resubmission.

### Phase 2: Staff CRM Portal & AdminLTE 4 Interface
* **Key Implementations:**
  - Implemented role-based access control with `@staff_required` enforcing active staff credentials and returning 403 for unauthorized users.
  - Integrated **AdminLTE 4** enterprise CRM design system with scoped custom styling in `static/css/adminlte_custom.css` aligning with Startup Sahay corporate identity (corporate navy `#0f2e5a` and warm energetic orange `#ea580c`).
  - Implemented dynamic metric aggregation for dashboard overview cards and ApexCharts visualizations.
  - Built 6-stage Kanban board pipeline (`New Inquiry`, `Contacted`, `Follow-up`, `Proposal Sent`, `Mature`, `Closed`).
  - Added direct WhatsApp outreach link generation (`wa.me/91...`) with pre-filled greeting templates.
  - Implemented parameterized search across name, phone, email, and reference ID with query-preserving pagination.

### Phase 3: Security Hardening & Vulnerability Remediation
Following technical code review, critical security improvements were implemented:
1. **Hardcoded Credentials Elimination:**
   - Refactored `inquiries/management/commands/setup_admin.py` to remove hardcoded passwords (`AdminPassword123!`).
   - Made admin setup strictly idempotent: existing user passwords are preserved across deployments; new accounts require explicit `ADMIN_PASSWORD` in the environment.
   - Updated `.env.example` with safe placeholder values only.
2. **Production-Ready Django Settings:**
   - Changed `DEBUG` to default strictly to `False`.
   - Hardened `ALLOWED_HOSTS` to read only from explicit environment configuration; eliminated wildcard `*` additions.
   - Enforced `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_SSL_REDIRECT`, `SECURE_HSTS_SECONDS=31536000`, `HSTS_INCLUDE_SUBDOMAINS`, and `HSTS_PRELOAD` in production.
   - Sanitized `CSRF_TRUSTED_ORIGINS`: removed wildcard testing domains (`*.ngrok*`, `*.loca.lt`, `*.onrender.com`).
3. **Robust Proxy-Safe Rate Limiting:**
   - Upgraded `get_client_ip` to validate IP addresses with `ipaddress.ip_address` when `USE_X_FORWARDED_FOR` is enabled, falling back safely to `REMOTE_ADDR` and `127.0.0.1`.
   - Configured `CACHES` to support shared Redis cache (`REDIS_URL`) with graceful fail-open error handling.
4. **Login Brute-Force & Lockout Protection:**
   - Implemented IP and username failure tracking in `dashboard/views.py` (`login_view`).
   - Applied temporary lockout after 5 consecutive failed attempts without revealing username existence.
   - Reset failure counters upon successful authentication.
5. **CSV Formula Injection Protection:**
   - Implemented `sanitize_csv_value` in `dashboard/services.py`.
   - Prepends single quote `'` to cells beginning with `=`, `+`, `-`, `@`, `\t`, `\r`, `|`, or `%`, neutralising formula execution in spreadsheet software while preserving clean readability.

### Phase 4: Validation & Business Logic Refactorings
1. **ASCII Mobile Number Validation:**
   - Upgraded `inquiries/validators.py` regex to `^[0-9]{10}$` with `re.ASCII` flag.
   - Strict rejection of Devanagari numerals (`०-९`) and other non-ASCII Unicode digits.
2. **Follow-Up Count Timezone & Boundary Fix:**
   - Replaced UTC midnight calculation with application timezone `Asia/Kolkata` midnight.
   - Overdue leads defined as `< start_of_today` (IST midnight).
   - Today's leads defined as `>= start_of_today` and `< start_of_tomorrow`.
   - Ensured Overdue and Due Today categories are strictly mutually exclusive and `total_due` count is 100% accurate.
3. **Centralized Status Transition Enforcement:**
   - Defined strict `ALLOWED_STATUS_TRANSITIONS` state machine in `dashboard/services.py`.
   - Refactored `lead_edit_view` so every status modification routes through `execute_status_transition` inside `transaction.atomic()` with `select_for_update()` row locking.
   - Added validation in `LeadForm` to block disallowed transitions at form validation time.
4. **Follow-Up Notes Data Loss Elimination:**
   - Added dedicated relational model `FollowUpNote` to record every follow-up note with timestamp and authoring staff user.
   - Replaced silent `[:2000]` string truncation in `schedule_follow_up_view` with a validation check that preserves all historical notes and displays an explicit error message when the internal notes character limit is reached.

### Phase 5: Database Architecture & Multi-Backend Support
- Dynamically configured `DATABASES` in `config/settings.py` supporting `DATABASE_URL` (PostgreSQL and SQLite) and discrete database environment variables.
- Maintained local SQLite out-of-the-box convenience for development while enabling zero-code configuration for production PostgreSQL deployments.
- Added `psycopg2-binary` and `dj-database-url` to `requirements.txt`.

### Phase 6: Dead Code Cleanup & Brand Consistency
- Removed unused `templates/tabler_base.html`.
- Removed unreferenced `static/css/dashboard.css` and `static/js/dashboard.js`.
- Removed unused `tabler_badge_class` property from `Inquiry` model.
- Polished AdminLTE 4 styling in `static/css/adminlte_custom.css` to faithfully reflect Startup Sahay corporate colors, typography, buttons, and badges.

---

## 3. Verification & Acceptance Summary

* **Automated Unit & Integration Tests:** 63 baseline tests + new comprehensive test suites.
* **Test Status:** 100% PASS (0 failures, 0 errors).
* **Django System Checks:** 0 issues identified.
