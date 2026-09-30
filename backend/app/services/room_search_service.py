"""
SAMS - Room Search Service
Logic tìm kiếm và bộ lọc phòng trống theo tiêu chí.
Tuân thủ FR-TENANT-06.
"""
from app.extensions import db
from app.models.room import Room, Building


class RoomSearchService:
    """
    Service tìm kiếm phòng trống với bộ lọc đa tiêu chí.
    Chỉ trả về phòng có status='vacant'.
    """

    @staticmethod
    def search_vacant_rooms(
        min_price: float | None = None,
        max_price: float | None = None,
        min_area: float | None = None,
        max_area: float | None = None,
        floor: int | None = None,
        has_balcony: bool | None = None,
        has_washing_machine: bool | None = None,
        has_kitchen: bool | None = None,
        has_parking: bool | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[dict], int]:
        """
        Tìm kiếm phòng trống theo bộ lọc.

        Returns:
            (danh sách phòng dict, tổng số kết quả)
        """
        query = (
            db.session.query(Room, Building)
            .join(Building, Room.building_id == Building.id)
            .filter(Room.status == "vacant")
        )

        # Áp dụng bộ lọc giá
        if min_price is not None:
            query = query.filter(Room.base_price >= min_price)
        if max_price is not None:
            query = query.filter(Room.base_price <= max_price)

        # Áp dụng bộ lọc diện tích
        if min_area is not None:
            query = query.filter(Room.area_sqm >= min_area)
        if max_area is not None:
            query = query.filter(Room.area_sqm <= max_area)

        # Áp dụng bộ lọc tầng
        if floor is not None:
            query = query.filter(Room.floor == floor)

        # Áp dụng bộ lọc tiện ích
        if has_balcony is not None:
            query = query.filter(Room.has_balcony == has_balcony)
        if has_washing_machine is not None:
            query = query.filter(Room.has_washing_machine == has_washing_machine)
        if has_kitchen is not None:
            query = query.filter(Room.has_kitchen == has_kitchen)
        if has_parking is not None:
            query = query.filter(Room.has_parking == has_parking)

        # Sắp xếp theo giá tăng dần
        query = query.order_by(Room.base_price.asc())

        # Đếm tổng
        total = query.count()

        # Phân trang
        results = query.offset((page - 1) * per_page).limit(per_page).all()

        rooms = []
        for room, building in results:
            room_dict = room.to_dict()
            room_dict["building_name"] = building.name
            room_dict["address"] = building.address
            rooms.append(room_dict)

        return rooms, total

    @staticmethod
    def get_room_with_active_contract(tenant_id: int) -> dict | None:
        """
        Lấy thông tin phòng và hợp đồng đang hoạt động của khách thuê.
        Tuân thủ FR-TENANT - khách chỉ được xem phòng của chính mình.

        Returns:
            dict chứa thông tin phòng và hợp đồng, hoặc None nếu không tìm thấy.
        """
        from app.models.contract import Contract
        from app.models.roommate import Roommate

        # Tìm hợp đồng đang active của tenant này
        contract = (
            db.session.query(Contract)
            .join(Room, Contract.room_id == Room.id)
            .filter(
                Contract.tenant_id == tenant_id,
                Contract.status == "active",
            )
            .first()
        )

        if not contract:
            return None

        room = contract.room
        building = room.building

        # Đếm số người đang ở cùng
        total_roommates = (
            db.session.query(Roommate)
            .filter(Roommate.room_id == room.id)
            .count()
        )

        return {
            "room_id": room.id,
            "room_number": room.room_number,
            "building_name": building.name if building else None,
            "building_address": building.address if building else None,
            "area_sqm": float(room.area_sqm) if room.area_sqm else None,
            "monthly_rent": float(contract.monthly_rent) if contract.monthly_rent else None,
            "deposit_amount": float(contract.deposit_amount) if contract.deposit_amount else None,
            "contract_id": contract.id,
            "start_date": contract.start_date.isoformat() if contract.start_date else None,
            "end_date": contract.end_date.isoformat() if contract.end_date else None,
            "contract_status": contract.status,
            "total_roommates": total_roommates,
        }
