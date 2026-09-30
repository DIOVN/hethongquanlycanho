"""
SAMS - Contract Model
Bảng contracts: Hợp đồng thuê phòng giữa chủ nhà và khách thuê.
"""
from datetime import datetime, timezone
from app.extensions import db


class Contract(db.Model):
    """
    Hợp đồng thuê phòng.
    Trạng thái: active | terminated | expired
    """
    __tablename__ = "contracts"

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(
        db.Integer,
        db.ForeignKey("rooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    deposit_amount = db.Column(db.Numeric(12, 2), nullable=False)
    monthly_rent = db.Column(db.Numeric(12, 2), nullable=False)
    status = db.Column(
        db.String(20),
        nullable=False,
        default="active",
        # Giá trị hợp lệ: active | terminated | expired
    )
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    terminated_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # --- Relationships ---
    room = db.relationship("Room", back_populates="contracts")
    tenant = db.relationship("User", back_populates="contracts")
    invoices = db.relationship("Invoice", back_populates="contract", lazy="dynamic")
    roommates = db.relationship("Roommate", back_populates="contract", lazy="dynamic")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "room_id": self.room_id,
            "tenant_id": self.tenant_id,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "deposit_amount": float(self.deposit_amount) if self.deposit_amount else None,
            "monthly_rent": float(self.monthly_rent) if self.monthly_rent else None,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "terminated_at": self.terminated_at.isoformat() if self.terminated_at else None,
        }

    def __repr__(self) -> str:
        return f"<Contract id={self.id} room_id={self.room_id} status={self.status}>"
