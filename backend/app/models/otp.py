"""
SAMS - OTP Verification Model
Quản lý mã xác thực OTP dùng cho Đăng ký tài khoản và Quên/Đặt lại mật khẩu.
Hỗ trợ kiểm soát thời gian hết hạn (expiration) và chống brute-force (max attempts).
"""
from datetime import datetime, timezone
from app.extensions import db


class OtpVerification(db.Model):
    """
    Bảng lưu trữ và xác thực mã OTP gửi qua email.
    
    purpose: 'register' | 'forgot_password'
    """
    __tablename__ = "otp_verifications"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    otp_code = db.Column(db.String(6), nullable=False)
    purpose = db.Column(
        db.String(30),
        nullable=False,
        # register | forgot_password
    )
    is_used = db.Column(db.Boolean, default=False, nullable=False)
    attempts = db.Column(db.Integer, default=0, nullable=False)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def is_valid(self) -> bool:
        """Kiểm tra mã OTP còn hiệu lực hay không."""
        now = datetime.now(timezone.utc)
        if self.is_used:
            return False
        if self.attempts >= 5:
            return False
        # Chuyển đổi expires_at sang timezone-aware nếu cần
        exp = self.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        return now < exp

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "purpose": self.purpose,
            "is_used": self.is_used,
            "attempts": self.attempts,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<OtpVerification id={self.id} email={self.email} purpose={self.purpose} is_used={self.is_used}>"
