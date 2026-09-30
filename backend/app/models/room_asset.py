"""
SAMS - Room Asset Model
Bảng room_assets: Kiểm kê đồ đạc/thiết bị trong phòng khi nhận phòng.
Phục vụ bảo vệ tiền cọc của cả hai bên khi trả phòng.
"""
from datetime import datetime, timezone
from app.extensions import db


class RoomAsset(db.Model):
    """
    Thiết bị/đồ đạc trong phòng thuê.
    Trạng thái: good | fair | damaged
    verified_by_tenant=True khi khách thuê đã xác nhận kiểm kê lúc nhận phòng.
    """
    __tablename__ = "room_assets"

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(
        db.Integer,
        db.ForeignKey("rooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    item_name = db.Column(db.String(200), nullable=False)
    brand_model = db.Column(db.String(200), nullable=True)
    serial_number = db.Column(db.String(100), nullable=True)
    condition = db.Column(
        db.String(20),
        nullable=False,
        default="good",
        # Giá trị hợp lệ: good | fair | damaged
    )
    # Ảnh chụp hiện trạng lúc nhận phòng để đối chiếu khi trả phòng
    image_url = db.Column(db.String(500), nullable=True)
    # Khóa sau khi khách xác nhận - không thể chỉnh sửa sau khi verified
    verified_by_tenant = db.Column(db.Boolean, default=False, nullable=False)
    verified_at = db.Column(db.DateTime(timezone=True), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # --- Relationships ---
    room = db.relationship("Room", back_populates="assets")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "room_id": self.room_id,
            "item_name": self.item_name,
            "brand_model": self.brand_model,
            "serial_number": self.serial_number,
            "condition": self.condition,
            "image_url": self.image_url,
            "verified_by_tenant": self.verified_by_tenant,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<RoomAsset id={self.id} item={self.item_name} condition={self.condition}>"
