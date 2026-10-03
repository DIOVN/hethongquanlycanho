"""
SAMS - Playwright E2E Test for SMTP & OTP Flows (Registration & Forgot Password)
"""
import os
import sys
import time
import shutil
import sqlite3
from playwright.sync_api import sync_playwright  # type: ignore

BASE_URL = "http://localhost:3000"
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "instance", "apartment.db"))
ARTIFACTS_DIR = None
SCREENSHOTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "playwright_screenshots"))
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

def get_latest_otp(email, purpose):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT otp_code FROM otp_verifications 
        WHERE email = ? AND purpose = ? AND is_used = 0
        ORDER BY id DESC LIMIT 1
    """, (email, purpose))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def save_artifact_screenshot(page, filename, description=""):
    local_path = os.path.join(SCREENSHOTS_DIR, filename)
    page.screenshot(path=local_path)
    # Also copy to artifacts dir
    artifact_path = os.path.join(ARTIFACTS_DIR, filename)
    shutil.copyfile(local_path, artifact_path)
    print(f"  ✓ {description} Screenshot: {filename}")

def run_otp_e2e():
    print("🚀 Bắt đầu Playwright E2E UI Test cho SMTP & Mã OTP...")
    test_ts = int(time.time())
    reg_username = f"user_e2e_{test_ts}"
    reg_email = f"user_e2e_{test_ts}@example.vn"
    reg_password = "SecurePassword2026@"
    new_password = "BrandNewPassword2026@"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 850})
        page = context.new_page()

        # -------------------------------------------------------------
        # TEST 1: Register Page - Step 1 Form
        # -------------------------------------------------------------
        print("\n[Step 1] Kiểm tra trang Đăng ký - Bước 1: Thông tin tài khoản...")
        page.goto(f"{BASE_URL}/register")
        page.wait_for_load_state("networkidle")
        time.sleep(0.5)
        save_artifact_screenshot(page, "otp_01_register_step1.png", "Trang Đăng ký Bước 1")

        # Điền thông tin bước 1
        page.fill("input[name='full_name']", "Hoàng Kim Ngân")
        page.fill("input[name='username']", reg_username)
        page.fill("input[name='email']", reg_email)
        page.fill("input[name='phone']", "0912345678")
        page.fill("input[name='password']", reg_password)
        page.fill("input[name='confirm_password']", reg_password)

        # Bấm Tiếp tục gửi OTP
        print("  -> Bấm gửi mã OTP đăng ký...")
        page.click("button:has-text('Tiếp tục & Nhận mã OTP qua Email')")
        
        # Chờ chuyển sang Bước 2
        page.wait_for_selector("text=Xác nhận & Hoàn tất Đăng ký", timeout=10000)
        time.sleep(0.5)
        save_artifact_screenshot(page, "otp_02_register_step2_otp.png", "Trang Đăng ký Bước 2 (Nhập OTP & đếm ngược)")

        # Lấy OTP từ DB
        otp_reg = get_latest_otp(reg_email, "register")
        print(f"  ✓ Đã lấy mã OTP Đăng ký từ Database: {otp_reg}")
        assert otp_reg is not None and len(otp_reg) == 6

        # Nhập 6 chữ số OTP
        page.fill("input[placeholder='000000']", otp_reg)

        # Bấm Hoàn tất đăng ký
        page.click("button:has-text('Xác nhận & Hoàn tất Đăng ký')")
        
        # Chờ chuyển hướng tới /dashboard
        page.wait_for_url("**/dashboard", timeout=15000)
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        save_artifact_screenshot(page, "otp_03_registered_dashboard.png", "Đăng ký thành công & Tự động vào Dashboard")
        print("  ✓ Đăng ký tài khoản với OTP thành công, auto-login vào Dashboard!")

        # -------------------------------------------------------------
        # TEST 2: Forgot Password - 3 Steps
        # -------------------------------------------------------------
        print("\n[Step 2] Kiểm tra Luồng Quên mật khẩu (/forgot-password)...")
        # Đi tới login
        page.goto(f"{BASE_URL}/login")
        page.wait_for_load_state("networkidle")

        # Bấm liên kết 'Quên mật khẩu?'
        page.click("a:has-text('Quên mật khẩu?')")
        page.wait_for_url("**/forgot-password", timeout=5000)
        time.sleep(0.5)
        save_artifact_screenshot(page, "otp_04_forgot_password_step1.png", "Trang Quên mật khẩu - Bước 1")

        # Điền email cần reset
        page.fill("input[name='email']", reg_email)
        page.click("button:has-text('Gửi mã xác thực OTP')")

        # Chờ bước 2: nhập OTP và mật khẩu mới
        page.wait_for_selector("text=Nhập mã OTP & Mật khẩu mới", timeout=10000)
        time.sleep(0.5)
        save_artifact_screenshot(page, "otp_05_forgot_password_step2.png", "Trang Quên mật khẩu - Bước 2")

        # Lấy OTP reset password
        otp_reset = get_latest_otp(reg_email, "forgot_password")
        print(f"  ✓ Đã lấy mã OTP Reset Password từ Database: {otp_reset}")
        assert otp_reset is not None and len(otp_reset) == 6

        # Nhập OTP và mật khẩu mới
        page.fill("input[name='otp_code']", otp_reset)
        page.fill("input[name='new_password']", new_password)
        page.fill("input[name='confirm_password']", new_password)

        page.click("button:has-text('Xác nhận Đặt lại Mật khẩu')")

        # Chờ bước 3: Màn hình thành công
        page.wait_for_selector("text=Đặt lại mật khẩu thành công!", timeout=10000)
        time.sleep(0.5)
        save_artifact_screenshot(page, "otp_06_forgot_password_success.png", "Trang Quên mật khẩu - Thành công")

        # Bấm nút 'Đăng nhập ngay'
        page.click("button:has-text('Đăng nhập ngay')")
        page.wait_for_url("**/login", timeout=5000)

        # Đăng nhập bằng mật khẩu mới
        page.fill("input[name='username'], input[type='text']", reg_username)
        page.fill("input[name='password'], input[type='password']", new_password)
        page.click("button[type='submit']")
        page.wait_for_url("**/dashboard", timeout=10000)
        print("  ✓ Đăng nhập thành công với mật khẩu mới!")

        browser.close()

    print("\n🎉 PLAYWRIGHT E2E CHO SMTP & MÃ OTP HOÀN TẤT XUẤT SẮC 100%!")

if __name__ == "__main__":
    run_otp_e2e()
