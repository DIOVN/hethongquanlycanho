"""
SAMS - Roommate Service
Logic quản lý nhân khẩu và người ở cùng trong phòng.
Tuân thủ FR-TENANT-07 và FR-LANDLORD-06.
"""
import re
from datetime import datetime, timezone

from app.extensions import db
from app.models.roommate import Roommate
from app.models.room import Room
from app.models.contract import Contract


# Regex kiểm tra CCCD Việt Nam: đúng 12 chữ số
_CCCD_REGEX = re.compile(r"^\d{12}$")


class RoommateService:
    """
    Service quản lý danh sách người ở cùng (roommates).
    Hỗ trợ khai báo tạm trú và quản lý biển số xe.
    """

    @staticmethod
    def validate_cccd(cccd: str) -> bool:
        """Kiểm tra CCCD hợp lệ: đúng 12 chữ số liên tiếp."""
        if not cccd:
            return True  # CCCD tùy chọn (có thể là CMND 9 số cũ)
        return bool(_CCCD_REGEX.match(cccd.strip()))

    @staticmethod
    def get_room_occupants(room_id: int) -> list[dict]:
        """
        Lấy danh sách tất cả người đang cư trú trong phòng.

        Args:
            room_id: ID phòng cần tra cứu.

        Returns:
            Danh sách roommates dạng dict, sắp xếp primary tenant lên đầu.
        """
        roommates = (
            db.session.query(Roommate)
            .filter(Roommate.room_id == room_id)
            .order_by(Roommate.is_primary_tenant.desc(), Roommate.created_at.asc())
            .all()
        )
        return [r.to_dict() for r in roommates]

    @staticmethod
    def register_occupant(
        room_id: int,
        full_name: str,
        phone: str | None = None,
        cccd_number: str | None = None,
        date_of_birth: str | None = None,  # ISO format: YYYY-MM-DD
        gender: str | None = None,
        hometown: str | None = None,
        vehicle_plate: str | None = None,
        is_primary_tenant: bool = False,
    ) -> tuple[Roommate | None, str | None]:
        """
        Đăng ký thêm thành viên mới vào phòng.

        Returns:
            (Roommate, None) nếu thành công.
            (None, error_code) nếu thất bại.
        """
        # Kiểm tra phòng tồn tại
        room = db.session.get(Room, room_id)
        if not room:
            return None, "ROOM_NOT_FOUND"

        # Kiểm tra CCCD hợp lệ
        if cccd_number and not RoommateService.validate_cccd(cccd_number):
            return None, "INVALID_CCCD_FORMAT"

        # Kiểm tra CCCD đã đăng ký chưa (tránh trùng lặp)
        if cccd_number:
            existing = (
                db.session.query(Roommate)
                .filter(
                    Roommate.cccd_number == cccd_number.strip(),
                    Roommate.room_id == room_id,
                )
                .first()
            )
            if existing:
                return None, "CCCD_ALREADY_REGISTERED"

        # Lấy contract_id hiện tại của phòng
        active_contract = (
            db.session.query(Contract)
            .filter(
                Contract.room_id == room_id,
                Contract.status == "active",
            )
            .first()
        )

        # Parse ngày sinh
        dob = None
        if date_of_birth:
            try:
                from datetime import date
                dob = date.fromisoformat(date_of_birth)
            except ValueError:
                return None, "INVALID_DATE_FORMAT"

        new_roommate = Roommate(
            room_id=room_id,
            contract_id=active_contract.id if active_contract else None,
            full_name=full_name.strip(),
            phone=phone.strip() if phone else None,
            cccd_number=cccd_number.strip() if cccd_number else None,
            date_of_birth=dob,
            gender=gender,
            hometown=hometown.strip() if hometown else None,
            vehicle_plate=vehicle_plate.strip().upper() if vehicle_plate else None,
            is_primary_tenant=is_primary_tenant,
            temporary_residence_status="pending",
        )

        db.session.add(new_roommate)
        db.session.commit()
        return new_roommate, None

    @staticmethod
    def update_residence_status(
        roommate_id: int,
        new_status: str,
    ) -> tuple[Roommate | None, str | None]:
        """
        Chủ nhà cập nhật trạng thái tạm trú sau khi nộp hồ sơ công an.

        Args:
            roommate_id: ID người ở cùng.
            new_status: 'pending' | 'registered' | 'rejected'

        Returns:
            (Roommate, None) nếu thành công.
            (None, error_code) nếu thất bại.
        """
        valid_statuses = {"pending", "registered", "rejected"}
        if new_status not in valid_statuses:
            return None, "INVALID_STATUS"

        roommate = db.session.get(Roommate, roommate_id)
        if not roommate:
            return None, "ROOMMATE_NOT_FOUND"

        roommate.temporary_residence_status = new_status
        db.session.commit()
        return roommate, None
