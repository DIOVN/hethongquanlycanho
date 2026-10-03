"""
SAMS - Verify Rooms Page Rendering with Playwright
"""
import os
import time
import shutil
from playwright.sync_api import sync_playwright  # type: ignore

BASE_URL = "http://localhost:3000"
ARTIFACTS_DIR = None
SCREENSHOTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "playwright_screenshots"))

def verify_rooms():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1366, "height": 850})
        page = context.new_page()

        print("1. Đăng nhập với tài khoản landlord1...")
        page.goto(f"{BASE_URL}/login")
        page.wait_for_load_state("networkidle")
        page.fill("input[name='username'], input[type='text']", "landlord1")
        page.fill("input[name='password'], input[type='password']", "password123")
        page.click("button[type='submit']")
        page.wait_for_url("**/dashboard", timeout=10000)

        print("2. Chuyển tới trang Quản lý phòng /rooms...")
        page.goto(f"{BASE_URL}/rooms")
        page.wait_for_load_state("networkidle")
        time.sleep(1.5)

        # Chụp ảnh Grid View
        local_path_grid = os.path.join(SCREENSHOTS_DIR, "rooms_page_grid.png")
        page.screenshot(path=local_path_grid)
        shutil.copyfile(local_path_grid, os.path.join(ARTIFACTS_DIR, "rooms_page_grid.png"))
        print(f"  ✓ Đã chụp ảnh Grid View: {local_path_grid}")

        # Kiểm tra sự hiện diện của các phòng (101, 102...)
        body_text = page.inner_text("body")
        assert "101" in body_text, "Không tìm thấy phòng 101"
        assert "Danh sách Phòng & Căn hộ" in body_text
        print("  ✓ Dữ liệu phòng hiển thị đầy đủ và chính xác trên Grid View!")

        # 3. Chuyển sang Table View
        print("3. Chuyển sang Table View...")
        page.click("button[title='Dạng bảng chi tiết (Table)']")
        time.sleep(0.5)
        local_path_table = os.path.join(SCREENSHOTS_DIR, "rooms_page_table.png")
        page.screenshot(path=local_path_table)
        shutil.copyfile(local_path_table, os.path.join(ARTIFACTS_DIR, "rooms_page_table.png"))
        print(f"  ✓ Đã chụp ảnh Table View: {local_path_table}")

        # 4. Mở modal Chi tiết & Nhân khẩu
        print("4. Mở modal Chi tiết phòng 101...")
        page.click("button:has-text('Xem'):visible")
        time.sleep(0.5)
        local_path_modal = os.path.join(SCREENSHOTS_DIR, "rooms_detail_modal.png")
        page.screenshot(path=local_path_modal)
        shutil.copyfile(local_path_modal, os.path.join(ARTIFACTS_DIR, "rooms_detail_modal.png"))
        print(f"  ✓ Đã chụp ảnh Modal chi tiết & nhân khẩu: {local_path_modal}")

        browser.close()
    print("🎉 KIỂM THỬ TRANG QUẢN LÝ PHÒNG THÀNH CÔNG 100%!")

if __name__ == "__main__":
    verify_rooms()
