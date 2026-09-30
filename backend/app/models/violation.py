"""
SAMS - RoomViolation Model
Bảng room_violations: Hệ thống cảnh báo vi phạm nội quy 3 cấp độ.
"""
from datetime import datetime, timezone
from app.extensions import db


class RoomViolation(db.Model):
    """
    Biên bản vi phạm nội quy căn hộ.
    
    Loại vi phạm: noise | hygiene | fire_safety | guest_policy | smoking | other
    Mức độ: reminder (Nhắc nhở) | warning (Cảnh cáo) | penalty (Phạt tiền)
    Trạng thái: pending | acknowledged | penalized | resolved
    """
    __tablename__ = "room_violations"

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(
        db.Integer,
        db.ForeignKey("rooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Người lập biên bản (chủ nhà hoặc admin)
    reported_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    violation_type = db.Column(
        db.String(30),
        nullable=False,
        # noise | hygiene | fire_safety | guest_policy | smoking | other
    )
    severity = db.Column(
        db.String(20),
        nullable=False,
        # reminder | warning | penalty
    )
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, nullable=True)
    # Ảnh chụp bằng chứng vi phạm
    evidence_image_url = db.Column(db.String(500), nullable=True)
    # Số tiền phạt (chỉ áp dụng khi severity='penalty')
    penalty_amount = db.Column(db.Numeric(12, 2), nullable=True, default=0)
    status = db.Column(
        db.String(20),
        nullable=False,
        default="pending",
        # pending | acknowledged | penalized | resolved
    )
    # Liên kết với invoice_item khi tiền phạt đã được cộng vào hóa đơn
    invoice_item_id = db.Column(
        db.Integer,
        db.ForeignKey("invoice_items.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    resolved_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # --- Relationships ---
    room = db.relationship("Room", back_populates="violations")
    reporter = db.relationship("User", back_populates="violations_reported")
    invoice_item = db.relationship("InvoiceItem", back_populates="violations")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "room_id": self.room_id,
            "reported_by": self.reported_by,
            "violation_type": self.violation_type,
            "severity": self.severity,
            "title": self.title,
            "description": self.description,
            "evidence_image_url": self.evidence_image_url,
            "penalty_amount": float(self.penalty_amount) if self.penalty_amount else 0.0,
            "status": self.status,
            "invoice_item_id": self.invoice_item_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }

    def __repr__(self) -> str:
        return (
            f"<RoomViolation id={self.id} room={self.room_id} "
            f"type={self.violation_type} severity={self.severity}>"
        )
