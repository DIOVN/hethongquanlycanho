"""
SAMS - Building & Room Models
Bảng buildings và rooms: Nền tảng quản lý bất động sản.
"""
from datetime import datetime, timezone
from decimal import Decimal
from app.extensions import db


class Building(db.Model):
    """
    Bảng tòa nhà - đơn vị quản lý cấp cao nhất.
    Một tòa nhà chứa nhiều phòng, nhiều chi phí vận hành và thông báo.
    """
    __tablename__ = "buildings"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(500), nullable=False)
    total_floors = db.Column(db.Integer, default=1, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # --- Relationships ---
    rooms = db.relationship("Room", back_populates="building", lazy="dynamic")
    expenses = db.relationship("Expense", back_populates="building", lazy="dynamic")
    announcements = db.relationship(
        "BulletinAnnouncement", back_populates="building", lazy="dynamic"
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "total_floors": self.total_floors,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<Building id={self.id} name={self.name}>"


class Room(db.Model):
    """
    Bảng phòng thuê - đơn vị cho thuê chính.
    Trạng thái: vacant | occupied | maintenance
    """
    __tablename__ = "rooms"

    id = db.Column(db.Integer, primary_key=True)
    building_id = db.Column(
        db.Integer,
        db.ForeignKey("buildings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    current_tenant_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    room_number = db.Column(db.String(20), nullable=False)
    floor = db.Column(db.Integer, nullable=True)
    base_price = db.Column(db.Numeric(12, 2), nullable=False)
    area_sqm = db.Column(db.Numeric(8, 2), nullable=True)
    status = db.Column(
        db.String(20),
        nullable=False,
        default="vacant",
        # Giá trị hợp lệ: vacant | occupied | maintenance
    )
    # Tiện ích phòng (dạng JSON string đơn giản để tránh thêm dependency)
    has_balcony = db.Column(db.Boolean, default=False)
    has_washing_machine = db.Column(db.Boolean, default=False)
    has_kitchen = db.Column(db.Boolean, default=False)
    has_parking = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # --- Relationships ---
    building = db.relationship("Building", back_populates="rooms")
    current_tenant = db.relationship("User", foreign_keys=[current_tenant_id])
    assets = db.relationship("RoomAsset", back_populates="room", lazy="dynamic")
    contracts = db.relationship("Contract", back_populates="room", lazy="dynamic")
    invoices = db.relationship("Invoice", back_populates="room", lazy="dynamic")
    utility_readings = db.relationship("UtilityReading", back_populates="room", lazy="dynamic")
    service_tickets = db.relationship("ServiceTicket", back_populates="room", lazy="dynamic")
    roommates = db.relationship("Roommate", back_populates="room", lazy="dynamic")
    violations = db.relationship("RoomViolation", back_populates="room", lazy="dynamic")

    def to_dict(self, include_building: bool = False) -> dict:
        result = {
            "id": self.id,
            "building_id": self.building_id,
            "room_number": self.room_number,
            "floor": self.floor,
            "base_price": float(self.base_price) if self.base_price else None,
            "area_sqm": float(self.area_sqm) if self.area_sqm else None,
            "status": self.status,
            "has_balcony": self.has_balcony,
            "has_washing_machine": self.has_washing_machine,
            "has_kitchen": self.has_kitchen,
            "has_parking": self.has_parking,
            "description": self.description,
            "current_tenant_id": self.current_tenant_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_building and self.building:
            result["building_name"] = self.building.name
            result["address"] = self.building.address
        if self.current_tenant:
            result["current_tenant_name"] = self.current_tenant.full_name
            result["current_tenant_phone"] = self.current_tenant.phone
            result["current_tenant_email"] = self.current_tenant.email
        return result

    def __repr__(self) -> str:
        return f"<Room id={self.id} number={self.room_number} status={self.status}>"
