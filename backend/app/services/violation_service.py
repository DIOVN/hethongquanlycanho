"""
SAMS - Violation Penalty Service
Quản lý cảnh báo vi phạm nội quy căn hộ 3 cấp độ (Nhắc nhở, Cảnh cáo, Phạt tiền).
Tuân thủ FR-LANDLORD-08: Tự động đưa các khoản phạt vào kỳ hóa đơn tiếp theo.
"""
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from app.extensions import db
from app.models.violation import RoomViolation
from app.models.room import Room
from app.models.invoice import InvoiceItem


VALID_CATEGORIES = {"noise", "hygiene", "fire_safety", "guest_policy", "smoking", "other"}
VALID_SEVERITIES = {"reminder", "warning", "penalty"}

# Mức phạt tiền mặc định theo loại vi phạm (VNĐ)
DEFAULT_PENALTIES = {
    "noise": Decimal("200000.00"),         # Hát karaoke, ồn ào sau 22h
    "hygiene": Decimal("100000.00"),       # Vứt rác bừa bãi, để rác trước cửa
    "fire_safety": Decimal("500000.00"),   # Quên khóa cổng, sạc xe điện sai nơi
    "guest_policy": Decimal("300000.00"),  # Dẫn người lạ ngủ qua đêm không khai báo
    "smoking": Decimal("200000.00"),       # Hút thuốc thang máy, khu vực cấm
    "other": Decimal("150000.00"),
}


class ViolationService:
    """Service xử lý vi phạm nội quy và phạt tiền."""

    @staticmethod
    def report_violation(
        room_id: int,
        violation_type: str,
        severity: str,
        title: str,
        description: str | None = None,
        reported_by: int | None = None,
        evidence_image_url: str | None = None,
        penalty_amount: float | Decimal | None = None,
    ) -> dict[str, Any]:
        """
        Tạo biên bản vi phạm mới cho căn hộ.

        Args:
            room_id: ID căn hộ vi phạm.
            violation_type: noise | hygiene | fire_safety | guest_policy | smoking | other.
            severity: reminder | warning | penalty.
            title: Tiêu đề vi phạm.
            description: Mô tả chi tiết hành vi vi phạm.
            reported_by: ID của người lập biên bản (chủ nhà hoặc admin).
            evidence_image_url: Đường dẫn ảnh bằng chứng.
            penalty_amount: Số tiền phạt (nếu là penalty).
        """
        room = db.session.get(Room, room_id)
        if not room:
            raise ValueError(f"Không tìm thấy phòng với ID {room_id}")

        v_type = violation_type.lower()
        if v_type not in VALID_CATEGORIES:
            raise ValueError(f"Loại vi phạm không hợp lệ: {violation_type}. Hợp lệ: {VALID_CATEGORIES}")

        sev = severity.lower()
        if sev not in VALID_SEVERITIES:
            raise ValueError(f"Mức độ vi phạm không hợp lệ: {severity}. Hợp lệ: {VALID_SEVERITIES}")

        # Tính tiền phạt nếu mức độ là phạt tiền
        calc_penalty = Decimal("0.00")
        if sev == "penalty":
            if penalty_amount is not None and float(penalty_amount) > 0:
                calc_penalty = Decimal(str(penalty_amount))
            else:
                calc_penalty = DEFAULT_PENALTIES.get(v_type, Decimal("200000.00"))

        violation = RoomViolation(
            room_id=room_id,
            reported_by=reported_by,
            violation_type=v_type,
            severity=sev,
            title=title.strip(),
            description=description.strip() if description else None,
            evidence_image_url=evidence_image_url,
            penalty_amount=calc_penalty,
            status="pending",
        )

        db.session.add(violation)
        db.session.commit()

        return violation.to_dict()

    @staticmethod
    def get_violations(
        room_id: int | None = None,
        status: str | None = None,
        severity: str | None = None,
    ) -> list[dict[str, Any]]:
        """Lấy danh sách các biên bản vi phạm theo bộ lọc."""
        query = db.session.query(RoomViolation)

        if room_id:
            query = query.filter(RoomViolation.room_id == room_id)
        if status:
            query = query.filter(RoomViolation.status == status)
        if severity:
            query = query.filter(RoomViolation.severity == severity)

        violations = query.order_by(RoomViolation.created_at.desc()).all()
        results = []
        for v in violations:
            data = v.to_dict()
            if v.room:
                data["room_number"] = v.room.room_number
            results.append(data)
        return results

    @staticmethod
    def get_violation_by_id(violation_id: int) -> dict[str, Any] | None:
        """Lấy chi tiết biên bản vi phạm theo ID."""
        violation = db.session.get(RoomViolation, violation_id)
        if not violation:
            return None
        data = violation.to_dict()
        if violation.room:
            data["room_number"] = violation.room.room_number
        return data

    @staticmethod
    def acknowledge_violation(violation_id: int) -> dict[str, Any]:
        """Khách thuê xác nhận đã đọc thông báo nhắc nhở/cảnh cáo vi phạm."""
        violation = db.session.get(RoomViolation, violation_id)
        if not violation:
            raise ValueError(f"Không tìm thấy biên bản vi phạm ID {violation_id}")

        if violation.status == "pending":
            violation.status = "acknowledged"
            db.session.commit()

        return violation.to_dict()

    @staticmethod
    def resolve_violation(violation_id: int) -> dict[str, Any]:
        """Đánh dấu vi phạm đã được giải quyết xong."""
        violation = db.session.get(RoomViolation, violation_id)
        if not violation:
            raise ValueError(f"Không tìm thấy biên bản vi phạm ID {violation_id}")

        violation.status = "resolved"
        violation.resolved_at = datetime.now(timezone.utc)
        db.session.commit()

        return violation.to_dict()

    @staticmethod
    def get_pending_penalties(room_id: int) -> list[RoomViolation]:
        """
        Lấy các khoản phạt chưa được đưa vào hóa đơn của phòng.
        Chỉ lấy severity='penalty' và invoice_item_id IS NULL.
        """
        return (
            db.session.query(RoomViolation)
            .filter(
                RoomViolation.room_id == room_id,
                RoomViolation.severity == "penalty",
                RoomViolation.invoice_item_id.is_(None),
                RoomViolation.status.in_(["pending", "acknowledged"]),
            )
            .all()
        )
