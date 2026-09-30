"""
SAMS - Invoice & InvoiceItem Models
Bảng invoices & invoice_items: Hóa đơn tiền phòng hàng tháng.
"""
from datetime import datetime, timezone
from app.extensions import db


class Invoice(db.Model):
    """
    Hóa đơn tiền phòng hàng tháng.
    Trạng thái: unpaid | paid | overdue | pending_verification
    """
    __tablename__ = "invoices"

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
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    status = db.Column(
        db.String(30),
        nullable=False,
        default="unpaid",
        # Giá trị hợp lệ: unpaid | paid | overdue | pending_verification
    )
    # Chuỗi payload VietQR chuẩn EMVCo - sinh tự động khi tạo hóa đơn
    vietqr_payload = db.Column(db.Text, nullable=True)
    # URL ảnh biên lai chuyển khoản do khách upload
    payment_slip_url = db.Column(db.String(500), nullable=True)
    payment_ref = db.Column(db.String(100), nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    paid_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # --- Relationships ---
    room = db.relationship("Room", back_populates="invoices")
    contract = db.relationship("Contract", back_populates="invoices")
    items = db.relationship(
        "InvoiceItem", back_populates="invoice", lazy="joined", cascade="all, delete-orphan"
    )

    def to_dict(self, include_items: bool = False) -> dict:
        result = {
            "id": self.id,
            "room_id": self.room_id,
            "contract_id": self.contract_id,
            "month": self.month,
            "year": self.year,
            "total_amount": float(self.total_amount) if self.total_amount else 0.0,
            "status": self.status,
            "vietqr_payload": self.vietqr_payload,
            "payment_slip_url": self.payment_slip_url,
            "payment_ref": self.payment_ref,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "paid_at": self.paid_at.isoformat() if self.paid_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_items:
            result["items"] = [item.to_dict() for item in self.items]
        return result

    def __repr__(self) -> str:
        return f"<Invoice id={self.id} room={self.room_id} {self.month}/{self.year} status={self.status}>"


class InvoiceItem(db.Model):
    """
    Chi tiết từng khoản tiền trong hóa đơn.
    Loại: rent | electricity | water | service | penalty
    """
    __tablename__ = "invoice_items"

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(
        db.Integer,
        db.ForeignKey("invoices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    item_type = db.Column(
        db.String(30),
        nullable=False,
        # Giá trị hợp lệ: rent | electricity | water | service | penalty
    )
    description = db.Column(db.String(300), nullable=True)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    quantity = db.Column(db.Numeric(10, 3), nullable=False, default=1)
    subtotal = db.Column(db.Numeric(12, 2), nullable=False, default=0)

    # --- Relationships ---
    invoice = db.relationship("Invoice", back_populates="items")
    # Liên kết với khoản phạt vi phạm (nếu là item_type='penalty')
    violations = db.relationship("RoomViolation", back_populates="invoice_item", lazy="dynamic")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "invoice_id": self.invoice_id,
            "item_type": self.item_type,
            "description": self.description,
            "unit_price": float(self.unit_price) if self.unit_price else 0.0,
            "quantity": float(self.quantity) if self.quantity else 1.0,
            "subtotal": float(self.subtotal) if self.subtotal else 0.0,
        }

    def __repr__(self) -> str:
        return f"<InvoiceItem id={self.id} type={self.item_type} subtotal={self.subtotal}>"
