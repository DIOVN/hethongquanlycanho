"""
SAMS - User Model
Bảng users: Lưu thông tin tài khoản của Khách thuê, Chủ nhà và Admin.
"""
from datetime import datetime, timezone
from app.extensions import db


class User(db.Model):
    """
    Bảng người dùng hệ thống với phân quyền Role-Based (RBAC).
    Role: 'admin' | 'landlord' | 'tenant'
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(
        db.String(20),
        nullable=False,
        default="tenant",
        # Giá trị hợp lệ: admin | landlord | tenant
    )
    full_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    cccd_number = db.Column(db.String(20), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # --- Relationships ---
    # Một user có thể là tenant trong nhiều hợp đồng (lịch sử)
    contracts = db.relationship("Contract", back_populates="tenant", lazy="dynamic")
    service_tickets = db.relationship("ServiceTicket", back_populates="tenant", lazy="dynamic")
    expenses = db.relationship("Expense", back_populates="recorded_by_user", lazy="dynamic")
    violations_reported = db.relationship(
        "RoomViolation", back_populates="reporter", lazy="dynamic"
    )
    announcements = db.relationship("BulletinAnnouncement", back_populates="author", lazy="dynamic")

    def to_dict(self) -> dict:
        """Serialize user sang dict, loại bỏ password_hash."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "phone": self.phone,
            "cccd_number": self.cccd_number,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username} role={self.role}>"
