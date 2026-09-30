"""
SAMS - Live Verification for Email OTP & Password Reset
Kiểm tra trực tiếp các API mới trên server đang chạy (http://127.0.0.1:5000)
"""
import requests
import os
import sqlite3

BASE = "http://127.0.0.1:5000/api/v1"
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "instance", "apartment.db"))

def get_latest_otp(email, purpose):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT otp_code FROM otp_verifications WHERE email = ? AND purpose = ? AND is_used = 0 ORDER BY created_at DESC LIMIT 1",
        (email.strip().lower(), purpose)
    )
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def test_otp_flows():
    print("=" * 65)
    print("🚀 Bắt đầu Kiểm tra Live: SMTP & Mã OTP Đăng ký / Quên mật khẩu")
    print("=" * 65)

    test_email = "nguyenhuu.thang97@gmail.com"
    test_user = "thangnh97"

    # Xóa user thử nghiệm cũ nếu có
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE username = ? OR email = ?", (test_user, test_email))
    c.execute("DELETE FROM otp_verifications WHERE email = ?", (test_email,))
    conn.commit()
    conn.close()

    # -------------------------------------------------------------
    # 1. GỬI MÃ OTP ĐĂNG KÝ TÀI KHOẢN
    # -------------------------------------------------------------
    print("\n[Bước 1] Gọi POST /auth/register/send-otp...")
    res1 = requests.post(f"{BASE}/auth/register/send-otp", json={"email": test_email})
    assert res1.status_code == 200, f"Gửi OTP thất bại: {res1.text}"
    print(f"  ✓ Gửi OTP thành công! Message: {res1.json().get('message')}")

    otp_register = get_latest_otp(test_email, "register")
    assert otp_register is not None, "Không tìm thấy OTP trong database!"
    print(f"  ✓ Mã OTP tạo ra trong hệ thống: >>> {otp_register} <<<")

    # -------------------------------------------------------------
    # 2. ĐĂNG KÝ VỚI MÃ OTP SAI
    # -------------------------------------------------------------
    print("\n[Bước 2] Thử đăng ký với mã OTP sai (999999)...")
    res_bad = requests.post(f"{BASE}/auth/register", json={
        "username": test_user,
        "email": test_email,
        "password": "Password123@",
        "full_name": "Nguyễn Hữu Thắng",
        "phone": "0912999888",
        "otp_code": "999999"
    })
    assert res_bad.status_code in (400, 422), f"Kỳ vọng thất bại nhưng nhận: {res_bad.status_code}"
    print(f"  ✓ Bắt lỗi OTP sai chính xác: {res_bad.json()['error']['code']} - {res_bad.json()['error']['message']}")

    # -------------------------------------------------------------
    # 3. ĐĂNG KÝ VỚI MÃ OTP ĐÚNG
    # -------------------------------------------------------------
    print("\n[Bước 3] Đăng ký với mã OTP chính xác...")
    res_ok = requests.post(f"{BASE}/auth/register", json={
        "username": test_user,
        "email": test_email,
        "password": "Password123@",
        "full_name": "Nguyễn Hữu Thắng",
        "phone": "0912999888",
        "otp_code": otp_register
    })
    assert res_ok.status_code == 201, f"Đăng ký thất bại: {res_ok.text}"
    user_created = res_ok.json()["data"]
    print(f"  ✓ Đăng ký thành công! ID={user_created['id']}, Tên={user_created['full_name']}")

    # -------------------------------------------------------------
    # 4. GỬI MÃ OTP QUÊN MẬT KHẨU
    # -------------------------------------------------------------
    print("\n[Bước 4] Gọi POST /auth/forgot-password...")
    res_forgot = requests.post(f"{BASE}/auth/forgot-password", json={"email": test_email})
    assert res_forgot.status_code == 200, f"Gửi OTP quên mật khẩu thất bại: {res_forgot.text}"
    print(f"  ✓ Gửi OTP quên mật khẩu thành công! Message: {res_forgot.json().get('message')}")

    otp_reset = get_latest_otp(test_email, "forgot_password")
    assert otp_reset is not None, "Không tìm thấy OTP forgot_password trong database!"
    print(f"  ✓ Mã OTP đặt lại mật khẩu: >>> {otp_reset} <<<")

    # -------------------------------------------------------------
    # 5. ĐẶT LẠI MẬT KHẨU MỚI
    # -------------------------------------------------------------
    new_password = "NewThangPassword2026@"
    print(f"\n[Bước 5] Gọi POST /auth/reset-password với mật khẩu mới: {new_password}...")
    res_reset = requests.post(f"{BASE}/auth/reset-password", json={
        "email": test_email,
        "otp_code": otp_reset,
        "new_password": new_password
    })
    assert res_reset.status_code == 200, f"Reset password thất bại: {res_reset.text}"
    print(f"  ✓ Đặt lại mật khẩu thành công! Message: {res_reset.json().get('message')}")

    # -------------------------------------------------------------
    # 6. ĐĂNG NHẬP THỬ BẰNG MẬT KHẨU CŨ & MẬT KHẨU MỚI
    # -------------------------------------------------------------
    print("\n[Bước 6] Đăng nhập bằng mật khẩu cũ (phải thất bại 401)...")
    res_old = requests.post(f"{BASE}/auth/login", json={"username": test_user, "password": "Password123@"})
    assert res_old.status_code == 401
    print("  ✓ Đăng nhập bằng mật khẩu cũ bị từ chối chính xác.")

    print("\n[Bước 7] Đăng nhập bằng mật khẩu mới...")
    res_new = requests.post(f"{BASE}/auth/login", json={"username": test_user, "password": new_password})
    assert res_new.status_code == 200, f"Đăng nhập mật khẩu mới thất bại: {res_new.text}"
    token_data = res_new.json()["data"]
    print(f"  ✓ Đăng nhập thành công! Nhận được JWT Token: {token_data['access_token'][:25]}...")

    print("\n" + "=" * 65)
    print("🎉 TẤT CẢ CÁC TÍNH NĂNG SMTP & MÃ OTP HOẠT ĐỘNG HOÀN HẢO 100%!")
    print("=" * 65)

if __name__ == "__main__":
    test_otp_flows()
