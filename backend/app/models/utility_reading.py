"""
SAMS - UtilityReading Model
Bảng utility_readings: Lưu chỉ số điện/nước kèm ảnh bằng chứng từ AI OCR.
"""
from datetime import datetime, timezone
from app.extensions import db


class UtilityReading(db.Model):
    """
    Chỉ số đồng hồ điện hoặc nước mỗi tháng.
    Loại: electricity | water
    Lưu URL ảnh chụp gốc để đối chiếu pháp lý khi tranh chấp.
    """
    __tablename__ = "utility_readings"

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(
        db.Integer,
        db.ForeignKey("rooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    meter_type = db.Column(
        db.String(20),
        nullable=False,
        # Giá trị hợp lệ: electricity | water
    )
    reading_value = db.Column(db.Numeric(12, 3), nullable=False)
    previous_value = db.Column(db.Numeric(12, 3), nullable=True)
    consumption = db.Column(db.Numeric(12, 3), nullable=True)
    # URL ảnh chụp đồng hồ công tơ - bằng chứng pháp lý không thể chối cãi
    image_proof_url = db.Column(db.String(500), nullable=True)
    # Độ tin cậy của kết quả AI OCR (0.0 - 1.0)
    ai_confidence = db.Column(db.Float, nullable=True)
    # Cờ đánh dấu chỉ số bất thường cần phúc tra
    flag_abnormal = db.Column(db.Boolean, default=False, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    recorded_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # --- Relationships ---
    room = db.relationship("Room", back_populates="utility_readings")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "room_id": self.room_id,
            "meter_type": self.meter_type,
            "reading_value": float(self.reading_value) if self.reading_value else None,
            "previous_value": float(self.previous_value) if self.previous_value else None,
            "consumption": float(self.consumption) if self.consumption else None,
            "image_proof_url": self.image_proof_url,
            "ai_confidence": self.ai_confidence,
            "flag_abnormal": self.flag_abnormal,
            "month": self.month,
            "year": self.year,
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None,
        }

    def __repr__(self) -> str:
        return (
            f"<UtilityReading id={self.id} room={self.room_id} "
            f"type={self.meter_type} reading={self.reading_value}>"
        )
