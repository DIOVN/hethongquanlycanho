"""
SAMS - Expense, BulletinAnnouncement, ServiceTicket Models
Các bảng hỗ trợ vận hành tòa nhà.
"""
from datetime import datetime, timezone
from app.extensions import db


class Expense(db.Model):
    """
    Chi phí vận hành tòa nhà (OpEx).
    Dùng để tính Lợi nhuận ròng = Doanh thu thực thu - Tổng chi phí.
    
    Loại: common_electricity | water | internet | cleaning | security | maintenance
    """
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    building_id = db.Column(
        db.Integer,
        db.ForeignKey("buildings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    recorded_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    expense_category = db.Column(
        db.String(30),
        nullable=False,
        # common_electricity | water | internet | cleaning | security | maintenance
    )
    title = db.Column(db.String(300), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    receipt_image_url = db.Column(db.String(500), nullable=True)
    expense_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # --- Relationships ---
    building = db.relationship("Building", back_populates="expenses")
    recorded_by_user = db.relationship("User", back_populates="expenses")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "building_id": self.building_id,
            "recorded_by": self.recorded_by,
            "expense_category": self.expense_category,
            "title": self.title,
            "amount": float(self.amount) if self.amount else 0.0,
            "receipt_image_url": self.receipt_image_url,
            "expense_date": self.expense_date.isoformat() if self.expense_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<Expense id={self.id} category={self.expense_category} amount={self.amount}>"


class BulletinAnnouncement(db.Model):
    """
    Thông báo bảng tin tòa nhà.
    Ưu tiên: normal | important | emergency
    """
    __tablename__ = "bulletin_announcements"

    id = db.Column(db.Integer, primary_key=True)
    building_id = db.Column(
        db.Integer,
        db.ForeignKey("buildings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    author_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    title = db.Column(db.String(300), nullable=False)
    content = db.Column(db.Text, nullable=False)
    priority = db.Column(
        db.String(20),
        nullable=False,
        default="normal",
        # normal | important | emergency
    )
    effective_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # --- Relationships ---
    building = db.relationship("Building", back_populates="announcements")
    author = db.relationship("User", back_populates="announcements")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "building_id": self.building_id,
            "author_id": self.author_id,
            "title": self.title,
            "content": self.content,
            "priority": self.priority,
            "effective_date": self.effective_date.isoformat() if self.effective_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<BulletinAnnouncement id={self.id} title={self.title} priority={self.priority}>"


class ServiceTicket(db.Model):
    """
    Yêu cầu sửa chữa / bảo trì từ khách thuê.
    Danh mục: repair | cleaning | security | other
    Mức độ: low | medium | high | urgent
    Trạng thái: pending | in_progress | resolved | cancelled
    """
    __tablename__ = "service_tickets"

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(
        db.Integer,
        db.ForeignKey("rooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    category = db.Column(
        db.String(20),
        nullable=False,
        # repair | cleaning | security | other
    )
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    priority = db.Column(
        db.String(20),
        nullable=False,
        default="medium",
        # low | medium | high | urgent
    )
    status = db.Column(
        db.String(20),
        nullable=False,
        default="pending",
        # pending | in_progress | resolved | cancelled
    )
    repair_cost = db.Column(db.Numeric(12, 2), nullable=True)
    resolved_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # --- Relationships ---
    room = db.relationship("Room", back_populates="service_tickets")
    tenant = db.relationship("User", back_populates="service_tickets")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "room_id": self.room_id,
            "tenant_id": self.tenant_id,
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "image_url": self.image_url,
            "priority": self.priority,
            "status": self.status,
            "repair_cost": float(self.repair_cost) if self.repair_cost else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<ServiceTicket id={self.id} title={self.title} status={self.status}>"
