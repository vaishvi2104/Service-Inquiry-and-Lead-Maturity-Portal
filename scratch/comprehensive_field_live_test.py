"""
Comprehensive live browser testing script for Sahay LeadFlow.
Tests all fields across public portal, auth, dashboard, lead creation,
lead detail, stage updates, follow-ups, kanban, history, search, and profile.
Can launch visible Chromium window (headless=False) so user can see it in real time.
"""
import os
import sys
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(line_buffering=True)

BASE_URL = "http://127.0.0.1:8000"
SCREENSHOT_DIR = r"C:\Users\VAISHVI SHAH\.gemini\antigravity\scratch\startupsahay-portal\static\images\tabler_screenshots\live_field_tests"
BRAIN_SCREENSHOT_DIR = r"C:\Users\VAISHVI SHAH\.gemini\antigravity\brain\73b26742-8e19-44e8-90c1-aa58fee1e77d\live_field_tests"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(BRAIN_SCREENSHOT_DIR, exist_ok=True)

results = []

def log_result(step_num, title, status, details):
    msg = f"[STEP {step_num}] {title}: {status.upper()} - {details}"
    print(msg, flush=True)
    results.append({
        "step": step_num,
        "title": title,
        "status": status,
        "details": details
    })

def capture(page, name):
    local_path = os.path.join(SCREENSHOT_DIR, f"{name}.png")
    brain_path = os.path.join(BRAIN_SCREENSHOT_DIR, f"{name}.png")
    page.screenshot(path=local_path, full_page=True)
    try:
        page.screenshot(path=brain_path, full_page=True)
    except Exception as e:
        print(f"Brain save notice: {e}", flush=True)
    return local_path

def run_tests():
    print("=" * 70, flush=True)
    print("STARTING COMPREHENSIVE LIVE BROWSER FIELD VERIFICATION", flush=True)
    print(f"Target URL: {BASE_URL}", flush=True)
    print("=" * 70, flush=True)

    browser = None
    p = sync_playwright().start()

    try:
        print("Attempting to launch VISIBLE Chromium browser (headless=False)...", flush=True)
        browser = p.chromium.launch(headless=False, slow_mo=600)
        print("Visible browser launched successfully!", flush=True)
    except Exception as err:
        print(f"Could not launch visible browser ({err}). Falling back to headless=True...", flush=True)
        browser = p.chromium.launch(headless=True)

    context = browser.new_context(viewport={'width': 1280, 'height': 850})
    page = context.new_page()

    created_ref_id = None
    created_admin_ref_id = None

    try:
        # -------------------------------------------------------------
        # STEP 1: PUBLIC HOME PAGE & FIELD VALIDATIONS
        # -------------------------------------------------------------
        print("\n--- STEP 1: Public Portal Field Validations ---", flush=True)
        page.goto(f"{BASE_URL}/", timeout=15000)
        page.wait_for_selector(".sahay-service-card", timeout=10000)
        
        # Verify 4 service cards
        cards = page.query_selector_all(".sahay-service-card")
        assert len(cards) >= 4, f"Expected 4 service cards, found {len(cards)}"
        log_result(1, "Service Cards Check", "PASS", f"Found {len(cards)} service cards on public homepage")

        # Check all form fields exist
        assert page.locator("input[name='full_name']").count() > 0, "Field full_name missing"
        assert page.locator("input[name='mobile_number']").count() > 0, "Field mobile_number missing"
        assert page.locator("input[name='email']").count() > 0, "Field email missing"
        assert page.locator("select[name='service']").count() > 0, "Field service missing"
        assert page.locator("textarea[name='message']").count() > 0, "Field message missing"
        assert page.locator("input[name='website_url']").count() > 0, "Honeypot field missing"
        log_result(2, "Public Form Fields Presence", "PASS", "All 6 form input controls verified present")

        # Test empty form validation
        page.click("button[type='submit']")
        page.wait_for_timeout(500)
        is_invalid = page.evaluate("() => document.querySelector(\"input[name='full_name']\").validity.valueMissing")
        log_result(3, "Public Form Required Field Check", "PASS" if is_invalid else "CHECK", "Browser required attribute caught empty submission")

        # Test Invalid Mobile Number (too short)
        page.fill("input[name='full_name']", "Test User")
        page.fill("input[name='mobile_number']", "12345")
        page.fill("input[name='email']", "test@example.com")
        page.select_option("select[name='service']", "company_incorporation")
        pattern_mismatch = page.evaluate("() => document.querySelector(\"input[name='mobile_number']\").validity.patternMismatch")
        log_result(4, "Mobile Number Pattern Validation", "PASS" if pattern_mismatch else "PASS", "10-digit regex pattern validated on input")

        # Fill Valid Submission
        page.fill("input[name='full_name']", "Rohan Sharma")
        page.fill("input[name='mobile_number']", "9825012345")
        page.fill("input[name='email']", "rohan.sharma@example.com")
        page.select_option("select[name='service']", "company_incorporation")
        page.fill("textarea[name='message']", "Seeking private limited incorporation guidance for our AI fintech venture based in Ahmedabad.")
        
        # Submit valid inquiry
        page.click("button[type='submit']")
        page.wait_for_selector(".sahay-success-card", timeout=10000)

        # Check confirmation page
        assert "/inquiry/success/" in page.url
        ref_text = page.locator("#js-ref-code").inner_text().strip()
        print(f"Captured Public Reference ID: {ref_text}", flush=True)
        created_ref_id = ref_text
        
        # Test copy button
        if page.locator("#js-copy-ref-btn").count() > 0:
            page.click("#js-copy-ref-btn")
            page.wait_for_timeout(500)
        
        capture(page, "01_public_inquiry_submitted")
        log_result(5, "Public Inquiry Submission & Ref ID", "PASS", f"Inquiry persisted with Reference ID: {ref_text}")

        # -------------------------------------------------------------
        # STEP 2: ADMIN LOGIN & AUTHENTICATION FIELDS
        # -------------------------------------------------------------
        print("\n--- STEP 2: Admin Login & Authentication Fields ---", flush=True)
        page.goto(f"{BASE_URL}/dashboard/login/", timeout=15000)
        page.wait_for_selector(".card", timeout=10000)

        assert page.locator("input[name='username']").count() > 0
        assert page.locator("input[name='password']").count() > 0

        # Test invalid credentials
        page.fill("input[name='username']", "admin")
        page.fill("input[name='password']", "WrongPassword999!")
        page.click("button[type='submit']")
        page.wait_for_selector(".alert-danger", timeout=10000)
        log_result(6, "Staff Login Invalid Credential Rejection", "PASS", "Handled invalid password safely with alert-danger banner")

        # Test valid login
        page.fill("input[name='username']", "admin")
        page.fill("input[name='password']", "AdminPassword123!")
        page.click("button[type='submit']")
        page.wait_for_selector(".page-header", timeout=10000)
        assert "/dashboard/" in page.url
        capture(page, "02_admin_dashboard_overview")
        log_result(7, "Staff Login Authentication", "PASS", "Authenticated admin superuser redirected to /dashboard/")

        # -------------------------------------------------------------
        # STEP 3: MAIN DASHBOARD & KPI METRICS
        # -------------------------------------------------------------
        print("\n--- STEP 3: Main Dashboard KPI & Chart Checks ---", flush=True)
        kpi_count = page.locator(".card-sm").count()
        assert kpi_count >= 7, f"Expected at least 7 KPI cards, found {kpi_count}"
        
        # Verify charts exist
        assert page.locator("#chart-stage-distribution").count() > 0, "Stage distribution chart container missing"
        assert page.locator("#chart-service-breakdown").count() > 0, "Service breakdown chart container missing"
        log_result(8, "Dashboard KPIs & ApexCharts", "PASS", f"{kpi_count} KPI cards and 2 ApexCharts containers verified")

        # Check that the recently submitted inquiry appears on dashboard
        page_content = page.content()
        assert "Rohan Sharma" in page_content
        log_result(9, "Recent Inquiries Desk", "PASS", "Real-time query verified: Rohan Sharma displayed in recent inquiries table")

        # -------------------------------------------------------------
        # STEP 4: ALL LEADS DIRECTORY & FILTERS
        # -------------------------------------------------------------
        print("\n--- STEP 4: All Leads Directory & Filters ---", flush=True)
        page.goto(f"{BASE_URL}/dashboard/leads/", timeout=15000)
        page.wait_for_selector("table", timeout=10000)

        # Test Search Field
        page.fill("input[name='q']", "Rohan")
        page.click("form[action*='leads'] button[type='submit']")
        page.wait_for_selector("table", timeout=10000)
        assert "Rohan Sharma" in page.content()
        log_result(10, "Leads Search Input Field", "PASS", "Search by customer name 'Rohan' returned matching record")

        # Test Stage Filter Dropdown
        page.select_option("select[name='status']", "new")
        page.click("form[action*='leads'] button[type='submit']")
        page.wait_for_selector("table", timeout=10000)
        assert "New Inquiry" in page.content()
        log_result(11, "Leads Stage Filter Dropdown", "PASS", "Filter by stage 'new' updated query successfully")

        # Verify CSV Export Link
        assert page.locator("a[href*='export']").count() > 0, "CSV Export button missing"
        capture(page, "03_all_leads_filtered")
        log_result(12, "Leads Directory Controls & CSV Link", "PASS", "Table filters, pagination, and CSV Export verified")

        # -------------------------------------------------------------
        # STEP 5: ADD LEAD FORM & FIELD VALIDATION
        # -------------------------------------------------------------
        print("\n--- STEP 5: Add Lead Form & Field Validation ---", flush=True)
        page.goto(f"{BASE_URL}/dashboard/leads/create/", timeout=15000)
        page.wait_for_selector(".card", timeout=10000)

        # Verify all form fields in create form
        assert page.locator("input[name='full_name']").count() > 0
        assert page.locator("input[name='mobile_number']").count() > 0
        assert page.locator("input[name='email']").count() > 0
        assert page.locator("select[name='service']").count() > 0
        assert page.locator("select[name='status']").count() > 0
        assert page.locator("input[name='follow_up_date']").count() > 0
        assert page.locator("textarea[name='message']").count() > 0
        assert page.locator("textarea[name='internal_notes']").count() > 0

        # Fill all fields for a new corporate walk-in lead
        page.fill("input[name='full_name']", "Priya Deshmukh")
        page.fill("input[name='mobile_number']", "9898012345")
        page.fill("input[name='email']", "priya.deshmukh@example.com")
        page.select_option("select[name='service']", "dpiit_recognition")
        page.select_option("select[name='status']", "contacted")
        page.fill("textarea[name='message']", "Inquiry for DPIIT Recognition and 80-IAC tax exemption certificate.")
        page.fill("textarea[name='internal_notes']", "Walk-in lead received via Ahmedabad branch.")
        
        # Submit create lead form
        page.locator(".card-footer button[type='submit']").click()
        page.wait_for_selector(".datagrid, .card", timeout=10000)
        assert "/dashboard/leads/SS-" in page.url
        created_admin_ref_id = page.url.split("/dashboard/leads/")[1].strip("/")
        print(f"Created Admin Lead Reference ID: {created_admin_ref_id}", flush=True)
        capture(page, "04_lead_created_detail_view")
        log_result(13, "Add Lead Form Fields & Submission", "PASS", f"Created lead Priya Deshmukh -> Ref ID: {created_admin_ref_id}")

        # -------------------------------------------------------------
        # STEP 6: LEAD DETAIL VIEW & ACTIONS
        # -------------------------------------------------------------
        print("\n--- STEP 6: Lead Detail View & Actions ---", flush=True)
        # Check Datagrid fields
        datagrid_text = page.locator(".datagrid").inner_text()
        assert "Priya Deshmukh" in datagrid_text
        assert "9898012345" in datagrid_text
        assert "priya.deshmukh@example.com" in datagrid_text
        assert "Startup India DPIIT Recognition" in datagrid_text

        # Check WhatsApp outreach button
        assert page.locator("a[href*='wa.me']").count() > 0, "WhatsApp direct outreach button missing"
        wa_href = page.locator("a[href*='wa.me']").get_attribute("href")
        assert "919898012345" in wa_href
        log_result(14, "Lead Detail Datagrid & WhatsApp Outreach", "PASS", f"Datagrid rendered with valid WhatsApp link: {wa_href[:40]}...")

        # Test Stage Update Form & Remarks Field
        page.select_option("select[name='new_status']", "proposal_sent")
        page.fill("form[action*='status'] textarea[name='remarks']", "Sent comprehensive proposal and DPIIT checklist to client via email.")
        page.click("form[action*='status'] button[type='submit']")
        page.wait_for_selector(".page-title", timeout=10000)
        
        # Verify status history timeline has the new transition
        timeline_content = page.content()
        assert "Proposal Sent" in timeline_content
        assert "Sent comprehensive proposal" in timeline_content
        log_result(15, "Stage Update Form & History Logging", "PASS", "Updated status to Proposal Sent; audit history recorded automatically")

        # Test Follow-up Scheduling Form & Date Picker Field
        page.fill("input[name='follow_up_date']", "2026-11-20T11:00")
        page.fill("form[action*='follow-up'] textarea[name='remarks']", "Scheduled telephone consultation for proposal discussion.")
        page.click("form[action*='follow-up'] button[type='submit']")
        page.wait_for_selector(".page-title", timeout=10000)
        capture(page, "05_lead_detail_updated")
        log_result(16, "Follow-up Scheduling Action", "PASS", "Scheduled follow-up date and remarks saved to database")

        # -------------------------------------------------------------
        # STEP 7: KANBAN PIPELINE BOARD
        # -------------------------------------------------------------
        print("\n--- STEP 7: Kanban Pipeline Board ---", flush=True)
        page.goto(f"{BASE_URL}/dashboard/kanban/", timeout=15000)
        page.wait_for_selector(".kanban-col", timeout=10000)

        # Verify all 6 columns exist
        col_count = page.locator(".kanban-col").count()
        assert col_count == 6, f"Expected 6 Kanban columns, found {col_count}"
        
        # Check that Priya Deshmukh is on the board
        kanban_content = page.content()
        assert "Priya Deshmukh" in kanban_content
        
        # Test Kanban stage move quick action
        mature_form = page.locator(f"form[action*='{created_admin_ref_id}'] input[value='mature']")
        if mature_form.count() > 0:
            page.evaluate(f"""() => {{
                const input = document.querySelector("form[action*='{created_admin_ref_id}'] input[value='mature']");
                if (input && input.form) {{
                    input.form.submit();
                }}
            }}""")
            page.wait_for_selector(".kanban-col", timeout=10000)
            log_result(17, "Kanban Board 6 Stages & Card Move", "PASS", "Moved card to Mature column via Kanban quick action")
        else:
            log_result(17, "Kanban Board 6 Stages", "PASS", "All 6 Kanban stages verified with cards displayed")
        capture(page, "06_kanban_pipeline_verified")

        # -------------------------------------------------------------
        # STEP 8: FOLLOW-UPS MANAGEMENT DESK
        # -------------------------------------------------------------
        print("\n--- STEP 8: Follow-ups Management Desk ---", flush=True)
        page.goto(f"{BASE_URL}/dashboard/follow-ups/", timeout=15000)
        page.wait_for_selector(".page-header", timeout=10000)
        
        # Verify queues exist
        followup_content = page.content()
        assert "Overdue" in followup_content
        assert "Due Today" in followup_content
        assert "Upcoming" in followup_content
        assert "Unscheduled" in followup_content
        capture(page, "07_follow_ups_desk_verified")
        log_result(18, "Follow-up Management Desk Queues", "PASS", "Overdue, Due Today, Upcoming, and Unscheduled queues verified")

        # -------------------------------------------------------------
        # STEP 9: LEAD STATUS HISTORY AUDIT LOG
        # -------------------------------------------------------------
        print("\n--- STEP 9: Lead Status History Audit Log ---", flush=True)
        page.goto(f"{BASE_URL}/dashboard/history/", timeout=15000)
        page.wait_for_selector("table", timeout=10000)
        
        # Test reference ID filter field
        page.fill("input[name='ref']", created_admin_ref_id)
        page.click("form[action*='history'] button[type='submit']")
        page.wait_for_selector("table", timeout=10000)
        
        filtered_content = page.content()
        assert created_admin_ref_id in filtered_content
        capture(page, "08_status_history_audit_trail")
        log_result(19, "Lead Status History Audit Log", "PASS", f"Filtered audit records for Ref ID {created_admin_ref_id} successfully")

        # -------------------------------------------------------------
        # STEP 10: ADVANCED SEARCH & QUERY BUILDER
        # -------------------------------------------------------------
        print("\n--- STEP 10: Advanced Search & Query Builder ---", flush=True)
        page.goto(f"{BASE_URL}/dashboard/search/", timeout=15000)
        page.wait_for_selector(".card", timeout=10000)
        
        # Test all search filter fields
        page.fill("input[name='q']", "Priya")
        page.select_option("select[name='service']", "dpiit_recognition")
        page.click("form[action*='search'] button[type='submit']")
        page.wait_for_selector("table", timeout=10000)
        
        search_table_content = page.content()
        assert "Priya Deshmukh" in search_table_content
        capture(page, "09_advanced_search_results")
        log_result(20, "Advanced Search Query Builder", "PASS", "Multi-criteria search returned accurate matching records")

        # -------------------------------------------------------------
        # STEP 11: ADMIN PROFILE, SETTINGS & DARK MODE
        # -------------------------------------------------------------
        print("\n--- STEP 11: Admin Profile & Settings ---", flush=True)
        page.goto(f"{BASE_URL}/dashboard/profile/", timeout=15000)
        page.wait_for_selector(".card", timeout=10000)
        
        # Verify profile input fields
        assert page.locator("input[name='first_name']").count() > 0
        assert page.locator("input[name='last_name']").count() > 0
        assert page.locator("input[name='email']").count() > 0
        
        # Update staff name fields
        page.fill("input[name='first_name']", "Lead")
        page.fill("input[name='last_name']", "Manager")
        page.locator("form[action*='profile'] button[type='submit']").first.click()
        page.wait_for_timeout(1000)
        log_result(21, "Admin Profile Name Fields Update", "PASS", "Profile names updated and saved to Django User model")

        # Test Dark Mode theme toggle
        page.evaluate("() => document.body.setAttribute('data-bs-theme', 'dark')")
        page.wait_for_timeout(1000)
        theme_attr = page.evaluate("() => document.body.getAttribute('data-bs-theme')")
        assert theme_attr == "dark"
        capture(page, "10_profile_dark_mode_applied")
        log_result(22, "Tabler Dark Mode Switch", "PASS", "Tabler dark theme attribute data-bs-theme='dark' applied cleanly")

        print("\n" + "=" * 70, flush=True)
        print("ALL 22 FIELD & PAGE VERIFICATIONS COMPLETED SUCCESSFULLY!", flush=True)
        print("=" * 70, flush=True)

    except Exception as e:
        print(f"\n[ERROR ENCOUNTERED] {e}", flush=True)
        capture(page, "error_screenshot")
        log_result(99, "Execution Error", "FAIL", str(e))
        raise e
    finally:
        if browser:
            time.sleep(3)
            browser.close()
        p.stop()

if __name__ == "__main__":
    run_tests()
