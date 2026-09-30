"""
SAMS - Auth Service
Logic xác thực người dùng, đăng ký và phát hành JWT tokens.
Tuân thủ FR-AUTH-01 và FR-AUTH-02.
"""
import re
import secrets
from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
from flask_jwt_extended import create_access_token, create_refresh_token
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.user import User
from app.models.otp import OtpVerification
from app.services.email_service import EmailService


# Khởi tạo Argon2 hasher với cấu hình bảo mật cao
_ph = PasswordHasher(
    time_cost=2,     # 2 iterations
    memory_cost=65536,  # 64MB
    parallelism=2,
    hash_len=32,
    salt_len=16,
)

# Regex kiểm tra số điện thoại Việt Nam
_PHONE_REGEX = re.compile(r"^(0|\+84)(3[2-9]|5[6-9]|7[0|6-9]|8[0-9]|9[0-9])[0-9]{7}$")


class AuthService:
    """Service xử lý toàn bộ logic xác thực và quản lý phiên làm việc."""

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Kiểm tra số điện thoại hợp lệ theo định dạng Việt Nam."""
        if not phone:
            return True  # SĐT tùy chọn
        return bool(_PHONE_REGEX.match(phone.strip()))

    @staticmethod
    def hash_password(plain_password: str) -> str:
        """Băm mật khẩu bằng Argon2 với salt ngẫu nhiên."""
        return _ph.hash(plain_password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Xác thực mật khẩu nhập vào với hash đã lưu.
        Trả về False thay vì throw exception để tránh timing attack.
        """
        try:
            return _ph.verify(hashed_password, plain_password)
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            return False

    @staticmethod
    def request_registration_otp(email: str) -> tuple[dict | None, str | None]:
        """
        Khởi tạo và gửi mã xác thực OTP 6 số qua email để đăng ký tài khoản.
        """
        clean_email = email.strip().lower()
        if not clean_email or "@" not in clean_email:
            return None, "INVALID_EMAIL"

        # Kiểm tra trùng lặp email với tài khoản đã có
        if User.query.filter_by(email=clean_email).first():
            return None, "EMAIL_EXISTS"

        # Sinh mã OTP 6 số ngẫu nhiên an toàn
        otp_code = f"{secrets.randbelow(1000000):06d}"
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

        # Hủy các OTP cũ chưa sử dụng cho email này
        OtpVerification.query.filter_by(
            email=clean_email, purpose="register", is_used=False
        ).update({"is_used": True})

        new_otp = OtpVerification(
            email=clean_email,
            otp_code=otp_code,
            purpose="register",
            expires_at=expires_at,
        )
        db.session.add(new_otp)
        db.session.commit()

        # Gửi email qua SMTP (hoặc fallback console)
        email_res = EmailService.send_otp_email(clean_email, otp_code, purpose="register")

        return {
            "email": clean_email,
            "expires_in_minutes": 10,
            "mode": email_res.get("mode"),
            "message": "Mã xác thực OTP đã được gửi đến email của bạn."
        }, None

    @staticmethod
    def register(
        username: str,
        email: str,
        password: str,
        full_name: str,
        phone: str | None = None,
        cccd_number: str | None = None,
        otp_code: str | None = None,
    ) -> tuple[User | None, str | None]:
        """
        Đăng ký tài khoản mới với role mặc định là 'tenant'.
        Nếu otp_code được truyền vào, kiểm tra tính hợp lệ của mã xác thực.
        """
        clean_email = email.strip().lower()

        # Kiểm tra trùng lặp username
        if User.query.filter_by(username=username.strip()).first():
            return None, "USERNAME_EXISTS"

        # Kiểm tra trùng lặp email
        if User.query.filter_by(email=clean_email).first():
            return None, "EMAIL_EXISTS"

        # Kiểm tra định dạng SĐT
        if phone and not AuthService.validate_phone(phone):
            return None, "INVALID_PHONE"

        # Xác thực mã OTP nếu có truyền vào
        if otp_code:
            otp_record = (
                OtpVerification.query
                .filter_by(email=clean_email, purpose="register", is_used=False)
                .order_by(OtpVerification.created_at.desc())
                .first()
            )
            if not otp_record or not otp_record.is_valid():
                return None, "OTP_EXPIRED"
            if otp_record.otp_code != otp_code.strip():
                otp_record.attempts += 1
                db.session.commit()
                return None, "INVALID_OTP"
            # Đánh dấu OTP đã được sử dụng thành công
            otp_record.is_used = True

        # Tạo user mới
        new_user = User(
            username=username.strip(),
            email=clean_email,
            password_hash=AuthService.hash_password(password),
            full_name=full_name.strip(),
            role="tenant",
            phone=phone.strip() if phone else None,
            cccd_number=cccd_number.strip() if cccd_number else None,
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            return new_user, None
        except IntegrityError:
            db.session.rollback()
            return None, "DATABASE_ERROR"

    @staticmethod
    def request_password_reset_otp(email: str) -> tuple[dict | None, str | None]:
        """
        Gửi mã OTP đặt lại mật khẩu cho tài khoản đã tồn tại.
        """
        clean_email = email.strip().lower()
        if not clean_email or "@" not in clean_email:
            return None, "INVALID_EMAIL"

        user = User.query.filter_by(email=clean_email).first()
        if not user:
            return None, "USER_NOT_FOUND"

        otp_code = f"{secrets.randbelow(1000000):06d}"
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

        # Hủy các OTP forgot_password cũ chưa sử dụng
        OtpVerification.query.filter_by(
            email=clean_email, purpose="forgot_password", is_used=False
        ).update({"is_used": True})

        new_otp = OtpVerification(
            email=clean_email,
            otp_code=otp_code,
            purpose="forgot_password",
            expires_at=expires_at,
        )
        db.session.add(new_otp)
        db.session.commit()

        email_res = EmailService.send_otp_email(clean_email, otp_code, purpose="forgot_password")

        return {
            "email": clean_email,
            "expires_in_minutes": 10,
            "mode": email_res.get("mode"),
            "message": "Mã xác thực đặt lại mật khẩu đã được gửi đến email của bạn."
        }, None

    @staticmethod
    def reset_password(email: str, otp_code: str, new_password: str) -> tuple[bool, str | None]:
        """
        Xác minh mã OTP và cập nhật mật khẩu mới cho người dùng.
        """
        clean_email = email.strip().lower()

        if len(new_password) < 8:
            return False, "WEAK_PASSWORD"

        otp_record = (
            OtpVerification.query
            .filter_by(email=clean_email, purpose="forgot_password", is_used=False)
            .order_by(OtpVerification.created_at.desc())
            .first()
        )
        if not otp_record or not otp_record.is_valid():
            return False, "OTP_EXPIRED"

        if otp_record.otp_code != otp_code.strip():
            otp_record.attempts += 1
            db.session.commit()
            return False, "INVALID_OTP"

        user = User.query.filter_by(email=clean_email).first()
        if not user:
            return False, "USER_NOT_FOUND"

        # Cập nhật mật khẩu mới và đánh dấu OTP đã dùng
        user.password_hash = AuthService.hash_password(new_password)
        otp_record.is_used = True
        db.session.commit()

        return True, None

    @staticmethod
    def login(username: str, password: str) -> tuple[dict | None, str | None]:
        """
        Xác thực thông tin đăng nhập và phát hành JWT tokens.

        Returns:
            (token_dict, None) nếu thành công.
            (None, error_code) nếu thất bại.
        """
        user = User.query.filter_by(username=username.strip()).first()

        if not user or not AuthService.verify_password(password, user.password_hash):
            return None, "INVALID_CREDENTIALS"

        # Gắn thông tin user vào JWT claims để dùng trong decorators
        additional_claims = {
            "role": user.role,
            "user_id": user.id,
            "username": user.username,
        }

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims=additional_claims,
        )
        refresh_token = create_refresh_token(
            identity=str(user.id),
            additional_claims=additional_claims,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": 86400,  # 24 giờ tính bằng giây
            "user": {
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "role": user.role,
            },
        }, None

    @staticmethod
    def get_user_by_id(user_id: int) -> User | None:
        """Lấy thông tin user theo ID (dùng trong decorator và endpoints)."""
        return db.session.get(User, user_id)
