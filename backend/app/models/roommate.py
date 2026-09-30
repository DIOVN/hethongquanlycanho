"""
SAMS - Roommate Model
Bảng roommates: Quản lý danh sách người ở cùng trong phòng.
Phục vụ khai báo tạm trú công an và quản lý bãi gửi xe.
"""
from datetime import datetime, timezone
from app.extensions import db


class Roommate(db.Model):
    """
    Người ở cùng trong phòng thuê.
    Bao gồm cả khách thuê đại diện hợp đồng (is_primary_tenant=True)
    và những người ở ghép (is_primary_tenant=False).

    Trạng thái tạm trú: pending | registered | rejected
    """
    __tablename__ = "roommates"

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(
        db.Integer,
        db.ForeignKey("rooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    contract_id = db.Column(
        db.Integer,
        db.ForeignKey("contracts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    full_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    cccd_number = db.Column(db.String(20), nullable=True, index=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(
        db.String(10), nullable=True
        # Giá trị hợp lệ: male | female | other
    )
    hometown = db.Column(db.String(200), nullable=True)
    # Biển số xe để cấp thẻ gửi xe và quản lý an ninh bãi đỗ
    vehicle_plate = db.Column(db.String(20), nullable=True)
    is_primary_tenant = db.Column(db.Boolean, default=False, nullable=False)
    temporary_residence_status = db.Column(
        db.String(20),
        default="pending",
        nullable=False,
        # Giá trị hợp lệ: pending | registered | rejected
    )
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # --- Relationships ---
    room = db.relationship("Room", back_populates="roommates")
    contract = db.relationship("Contract", back_populates="roommates")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "room_id": self.room_id,
            "contract_id": self.contract_id,
            "full_name": self.full_name,
            "phone": self.phone,
            "cccd_number": self.cccd_number,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "gender": self.gender,
            "hometown": self.hometown,
            "vehicle_plate": self.vehicle_plate,
            "is_primary_tenant": self.is_primary_tenant,
            "temporary_residence_status": self.temporary_residence_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return (
            f"<Roommate id={self.id} name={self.full_name} "
            f"room_id={self.room_id} primary={self.is_primary_tenant}>"
        )
