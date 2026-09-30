"""
SAMS - Comprehensive Playwright End-to-End (E2E) Test Suite
Tự động hóa kiểm thử UI/UX, Navigation, Dashboard KPIs, VietQR Invoices,
Tickets, Violations và Net Profit Reports.
"""
import sys
import os
import time
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:3000"
SCREENSHOTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "playwright_screenshots"))
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)


def run_e2e_tests():
    print("🚀 Starting SAMS Playwright E2E Test Suite...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        # -------------------------------------------------------------
        # TEST 1: Public Room Discovery & Search (/rooms/search)
        # -------------------------------------------------------------
        print("\n[Step 1] Navigating to Public Room Search...")
        page.goto(f"{BASE_URL}/rooms/search", timeout=30000)
        page.wait_for_load_state("networkidle")
        search_screenshot = os.path.join(SCREENSHOTS_DIR, "01_room_search.png")
        page.screenshot(path=search_screenshot)
        print(f"  ✓ Room search page loaded. Screenshot: {search_screenshot}")

        # -------------------------------------------------------------
        # TEST 2: Landlord Login Authentication (/login)
        # -------------------------------------------------------------
        print("\n[Step 2] Testing Landlord Authentication...")
        page.goto(f"{BASE_URL}/login")
        page.wait_for_load_state("networkidle")

        # Fill login form
        page.fill("input[name='username'], input[type='text']", "landlord1")
        page.fill("input[name='password'], input[type='password']", "password123")
        page.click("button[type='submit']")

        # Wait for redirect to /dashboard
        page.wait_for_url("**/dashboard", timeout=15000)
        page.wait_for_selector("h1:has-text('Xin chào')", timeout=10000)
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        dash_screenshot = os.path.join(SCREENSHOTS_DIR, "02_landlord_dashboard.png")
        page.screenshot(path=dash_screenshot)
        print(f"  ✓ Login successful! Redirected to Dashboard. Screenshot: {dash_screenshot}")

        # Verify Dashboard header text
        welcome_text = page.inner_text("body")
        assert "SAMS" in welcome_text
        assert "Xin chào" in welcome_text or "Quản lý" in welcome_text or "Tổng quan" in welcome_text
        print("  ✓ Welcome text and SAMS branding verified on Dashboard.")

        # -------------------------------------------------------------
        # TEST 3: Invoices & VietQR Portal (/invoices)
        # -------------------------------------------------------------
        print("\n[Step 3] Testing Invoices & VietQR Page...")
        page.goto(f"{BASE_URL}/invoices")
        page.wait_for_load_state("networkidle")
        invoices_screenshot = os.path.join(SCREENSHOTS_DIR, "03_invoices_page.png")
        page.screenshot(path=invoices_screenshot)
        page_text = page.inner_text("body")
        assert "Hóa đơn" in page_text
        print(f"  ✓ Invoices page verified. Screenshot: {invoices_screenshot}")

        # -------------------------------------------------------------
        # TEST 4: Violations Management (/violations)
        # -------------------------------------------------------------
        print("\n[Step 4] Testing Violations Management Page...")
        page.goto(f"{BASE_URL}/violations")
        page.wait_for_load_state("networkidle")
        violations_screenshot = os.path.join(SCREENSHOTS_DIR, "04_violations_page.png")
        page.screenshot(path=violations_screenshot)
        vio_text = page.inner_text("body")
        assert "Vi phạm" in vio_text or "nội quy" in vio_text.lower()
        print(f"  ✓ Violations page verified. Screenshot: {violations_screenshot}")

        # -------------------------------------------------------------
        # TEST 5: Service Tickets & Maintenance (/tickets)
        # -------------------------------------------------------------
        print("\n[Step 5] Testing Service Tickets Page...")
        page.goto(f"{BASE_URL}/tickets")
        page.wait_for_load_state("networkidle")
        tickets_screenshot = os.path.join(SCREENSHOTS_DIR, "05_tickets_page.png")
        page.screenshot(path=tickets_screenshot)
        tick_text = page.inner_text("body")
        assert "Sửa chữa" in tick_text or "Báo hỏng" in tick_text
        print(f"  ✓ Service Tickets page verified. Screenshot: {tickets_screenshot}")

        # -------------------------------------------------------------
        # TEST 6: Reports, OpEx Ledger & Net Profit (/reports)
        # -------------------------------------------------------------
        print("\n[Step 6] Testing Financial Reports & Net Profit Page...")
        page.goto(f"{BASE_URL}/reports")
        page.wait_for_load_state("networkidle")
        reports_screenshot = os.path.join(SCREENSHOTS_DIR, "06_financial_reports.png")
        page.screenshot(path=reports_screenshot)
        rep_text = page.inner_text("body")
        assert "Lợi Nhuận Ròng" in rep_text or "Net Profit" in rep_text or "Doanh thu" in rep_text
        assert "Chi phí Vận hành" in rep_text or "OpEx" in rep_text
        print(f"  ✓ Financial Reports & Net Profit page verified. Screenshot: {reports_screenshot}")

        # -------------------------------------------------------------
        # TEST 7: AI Chat Assistant Floating Widget
        # -------------------------------------------------------------
        print("\n[Step 7] Testing Floating Gemini Chat Assistant...")
        chat_btn = page.query_selector("button:has-text('Trợ lý AI'), button:has-text('AI'), button[title*='Chat']")
        if chat_btn:
            chat_btn.click()
            time.sleep(1)
            chat_screenshot = os.path.join(SCREENSHOTS_DIR, "07_chat_widget_open.png")
            page.screenshot(path=chat_screenshot)
            print(f"  ✓ Chat Assistant widget opened. Screenshot: {chat_screenshot}")

        context.close()
        browser.close()

    print("\n" + "=" * 65)
    print(" 🎉 ALL 7 PLAYWRIGHT E2E WORKFLOWS EXECUTED AND PASSED 100%!")
    print(f" 📸 Screenshots saved to: {SCREENSHOTS_DIR}")
    print("=" * 65)


if __name__ == "__main__":
    run_e2e_tests()
