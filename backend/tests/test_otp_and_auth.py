"""
SAMS - Unit & Integration Test Suite for OTP & Password Reset
Kiểm thử toàn diện quy trình gửi mã OTP qua email/console, đăng ký tài khoản có OTP,
và quy trình quên/đặt lại mật khẩu.
"""
from datetime import datetime, timedelta, timezone
import pytest
from app.extensions import db
from app.models.user import User
from app.models.otp import OtpVerification
from app.services.auth_service import AuthService
from app.services.email_service import EmailService


def test_email_service_fallback():
    """Kiểm tra EmailService tự động fallback mock console an toàn."""
    res = EmailService.send_otp_email("test_resident@gmail.com", "123456", purpose="register")
    assert res["success"] is True
    assert res["recipient"] == "test_resident@gmail.com"
    assert "otp_code" in res or res.get("mode") in ("mock_console", "fallback_console", "smtp_live")


def test_registration_otp_lifecycle(client, app):
    """Kiểm tra vòng đời gửi OTP và đăng ký tài khoản mới."""
    test_email = "linh.dan99@gmail.com"

    # 1. Yêu cầu gửi OTP đăng ký
    res_otp = client.post("/api/v1/auth/register/send-otp", json={"email": test_email})
    assert res_otp.status_code == 200
    assert res_otp.get_json()["success"] is True

    # 2. Truy vấn mã OTP trong database
    with app.app_context():
        otp_rec = (
            OtpVerification.query
            .filter_by(email=test_email, purpose="register", is_used=False)
            .order_by(OtpVerification.created_at.desc())
            .first()
        )
        assert otp_rec is not None
        assert len(otp_rec.otp_code) == 6
        assert otp_rec.is_valid() is True
        otp_code = otp_rec.otp_code

    # 3. Đăng ký với mã OTP sai
    res_bad = client.post(
        "/api/v1/auth/register",
        json={
            "username": "linhdan99",
            "email": test_email,
            "password": "Password123@",
            "full_name": "Đặng Linh Đan",
            "phone": "0988112233",
            "otp_code": "000000"
        }
    )
    assert res_bad.status_code == 422
    assert res_bad.get_json()["error"]["code"] == "INVALID_OTP"

    # 4. Đăng ký với mã OTP đúng
    res_ok = client.post(
        "/api/v1/auth/register",
        json={
            "username": "linhdan99",
            "email": test_email,
            "password": "Password123@",
            "full_name": "Đặng Linh Đan",
            "phone": "0988112233",
            "otp_code": otp_code
        }
    )
    assert res_ok.status_code == 201
    assert res_ok.get_json()["success"] is True
    assert res_ok.get_json()["data"]["username"] == "linhdan99"

    # 5. Kiểm tra OTP đã chuyển thành is_used=True
    with app.app_context():
        otp_used = db.session.get(OtpVerification, otp_rec.id)
        assert otp_used.is_used is True

    # 6. Đăng nhập với tài khoản vừa tạo
    res_login = client.post(
        "/api/v1/auth/login",
        json={"username": "linhdan99", "password": "Password123@"}
    )
    assert res_login.status_code == 200
    assert "access_token" in res_login.get_json()["data"]


def test_forgot_and_reset_password_flow(client, app):
    """Kiểm tra quy trình quên mật khẩu và đặt lại mật khẩu với OTP."""
    user_email = "quocdung.reset@gmail.com"

    with app.app_context():
        user = User(
            username="quocdung_reset",
            email=user_email,
            password_hash=AuthService.hash_password("OldPassword123@"),
            full_name="Phạm Quốc Dũng",
            role="landlord",
            phone="0909999888"
        )
        db.session.add(user)
        db.session.commit()

    # 1. Yêu cầu OTP quên mật khẩu
    res_req = client.post("/api/v1/auth/forgot-password", json={"email": user_email})
    assert res_req.status_code == 200
    assert res_req.get_json()["success"] is True

    # 2. Lấy OTP trong DB
    with app.app_context():
        otp_rec = (
            OtpVerification.query
            .filter_by(email=user_email, purpose="forgot_password", is_used=False)
            .order_by(OtpVerification.created_at.desc())
            .first()
        )
        assert otp_rec is not None
        otp_code = otp_rec.otp_code

    # 3. Đặt lại mật khẩu với OTP đúng
    res_reset = client.post(
        "/api/v1/auth/reset-password",
        json={
            "email": user_email,
            "otp_code": otp_code,
            "new_password": "NewSecretPassword2026@"
        }
    )
    assert res_reset.status_code == 200
    assert res_reset.get_json()["success"] is True

    # 4. Đăng nhập bằng mật khẩu cũ phải THẤT BẠI
    res_old = client.post(
        "/api/v1/auth/login",
        json={"username": "quocdung_reset", "password": "OldPassword123@"}
    )
    assert res_old.status_code == 401

    # 5. Đăng nhập bằng mật khẩu mới phải THÀNH CÔNG
    res_new = client.post(
        "/api/v1/auth/login",
        json={"username": "quocdung_reset", "password": "NewSecretPassword2026@"}
    )
    assert res_new.status_code == 200
    assert "access_token" in res_new.get_json()["data"]
