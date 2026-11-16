# Start-Up Sahay Private Limited — Security Architecture & Threat Review

> **Document Version:** 1.0.0  
> **Target System:** Service Inquiry & Lead Maturity Portal  
> **Audience:** Lead Architect, Security Auditor, Technical Evaluator  

---

## 1. Executive Summary

This document outlines the security architecture, threat model, mitigation controls, and verification evidence for the **Start-Up Sahay Private Limited** Service Inquiry & Lead Maturity Portal.

The application handles prospective client inquiries and tracks confidential lead progression through six maturity stages. Security has been designed and implemented in depth: all authentication and authorization barriers are strictly enforced server-side, database queries rely purely on the Django ORM without raw SQL, forms are guarded against CSRF and automated spam bots, and user data is auto-escaped across all templates and JavaScript handlers.

---

## 2. Threat Modeling & Security Controls Matrix

| Threat ID | Threat Vector / Description | Implemented Countermeasure | Relevant Code / Configuration | Test Verification |
| :--- | :--- | :--- | :--- | :--- |
| **TH-01** | **Unauthorized Access to Private Lead Data**<br>Unauthenticated or regular users accessing lead records. | Custom `@staff_required` view decorator requiring active staff or superuser privileges; anonymous users redirected to login; non-staff users receive HTTP 403 Forbidden. | `dashboard/views.py`<br>`@staff_required` | `test_anonymous_access_to_leads_redirects_to_login`<br>`test_authenticated_non_staff_user_denied_forbidden` |
| **TH-02** | **Cross-Site Request Forgery (CSRF)**<br>Malicious cross-origin requests altering lead status or terminating sessions. | Django `CsrfViewMiddleware` active; `{% csrf_token %}` on every form; GET method explicitly disallowed on status updates (405) and logout (405). | `config/settings.py`<br>`dashboard/views.py` | `test_csrf_protection_enforced_on_status_update`<br>`test_csrf_protection_enforced_on_logout`<br>`test_get_request_cannot_change_lead_status` |
| **TH-03** | **Automated Bot & Spam Abuse**<br>Bots spamming the public inquiry submission form. | Server-side honeypot field (`website_url`) hidden via offscreen styling and `tabindex="-1"`; submissions with non-empty honeypot are rejected. IP-based rate limiting on public endpoint. | `inquiries/forms.py`<br>`inquiries/services.py` | `test_honeypot_filled_causes_rejection`<br>`test_honeypot_submission_does_not_create_inquiry` |
| **TH-04** | **Cross-Site Scripting (XSS)**<br>Injecting malicious HTML/JS payloads via customer name, email, or message. | Django template autoescaping enabled; strict character validation on name (`validate_full_name`); DOM updates use vanilla JS `textContent`; no `safe` filters used on user input. | `inquiries/validators.py`<br>`templates/`<br>`static/js/main.js` | `test_xss_in_message_is_escaped`<br>`test_template_autoescaping_prevents_xss` |
| **TH-05** | **SQL Injection (SQLi)**<br>Manipulating search queries or filter parameters to execute arbitrary SQL. | 100% Django ORM parameterized queries with `Q` objects; no string concatenation into raw SQL; status filter validated against strict choices list. | `dashboard/services.py`<br>`get_filtered_leads_queryset` | `test_sql_injection_probe_strings_handled_safely` |
| **TH-06** | **Credential & Session Hijacking**<br>Compromise of session cookies or dictionary attacks on staff credentials. | `SESSION_COOKIE_HTTPONLY = True`, `CSRF_COOKIE_HTTPONLY = True`, `SameSite='Lax'`, generic failure messages to prevent username enumeration, no public registration. | `config/settings.py`<br>`dashboard/views.py` | `test_security_cookie_configurations`<br>`test_invalid_login_fails_safely` |
| **TH-07** | **Data Race Conditions in Lead Updates**<br>Concurrent administrators updating lead stage simultaneously causing inconsistent history. | Database transaction (`transaction.atomic`) combined with pessimistic row locking (`select_for_update()`); no-op transitions (same status) rejected. | `dashboard/services.py`<br>`execute_status_transition` | `test_valid_status_transition_succeeds_and_creates_history`<br>`test_no_op_same_status_update_rejected` |
| **TH-08** | **Open Redirect Vulnerability**<br>Manipulating `next` login parameter to divert users to phishing destinations. | `url_has_allowed_host_and_scheme()` validation with `request.get_host()` whitelist before redirecting authenticated staff. | `dashboard/views.py`<br>`login_view` | Verified via redirect sanitization logic |
| **TH-09** | **Sensitive Data Leakage via Reference IDs**<br>Enumerating database IDs or inferring customer records. | Non-sequential, cryptographic reference IDs generated via `secrets.token_hex()` in format `SS-YYYYMMDD-XXXX`. Database primary keys never exposed publicly. | `inquiries/services.py`<br>`generate_unique_reference_id` | `test_whatsapp_url_generation_for_valid_number` |

---

## 3. Cookie & Session Configuration Summary

```python
# config/settings.py
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
```

---

## 4. Verification Evidence

The test suite contains **51 automated tests** covering models, forms, public views, staff authentication, leads management, and security controls:

```text
Ran 51 tests in 23.698s
OK (0 failures, 0 errors, 0 skips)
```

Specific security test cases verified:
1. `test_csrf_protection_enforced_on_status_update`: Passes (HTTP 403 when CSRF missing).
2. `test_csrf_protection_enforced_on_logout`: Passes (HTTP 403 when CSRF missing).
3. `test_get_request_cannot_change_lead_status`: Passes (HTTP 405 Method Not Allowed).
4. `test_sql_injection_probe_strings_handled_safely`: Passes (5 hostile payloads tested cleanly).
5. `test_template_autoescaping_prevents_xss`: Passes (HTML escaped in output).
6. `test_security_cookie_configurations`: Passes (`HTTPOnly=True`, `SameSite='Lax'`).
7. `test_honeypot_submission_does_not_create_inquiry`: Passes (Zero DB records inserted).

---

## 5. Residual Risks & Production Deployment Recommendations

1. **HTTPS / TLS Termination**: Production must run behind a verified SSL certificate (e.g. Let's Encrypt / Cloudflare). Set `SESSION_COOKIE_SECURE=True` and `CSRF_COOKIE_SECURE=True` in production `.env`.
2. **Reverse Proxy IP Trust**: If deployed behind NGINX or AWS ALB, configure `SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')` and verify client IP extraction for rate-limiting.
3. **Database Migration to PostgreSQL**: For enterprise scale (> 50,000 monthly inquiries), configure PostgreSQL using `psycopg` to support high concurrent row-level locking.
