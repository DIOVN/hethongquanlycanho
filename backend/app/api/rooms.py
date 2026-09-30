"""
SAMS - Room API Controller
Endpoints xem và tìm kiếm phòng.
GET /api/v1/rooms (danh sách cho landlord)
GET /api/v1/rooms/search (tìm kiếm phòng trống - public)
GET /api/v1/rooms/my-room (khách thuê xem phòng của mình)
GET /api/v1/rooms/:id (chi tiết phòng)
Tuân thủ API.md §3.2
"""
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity

from app.services.room_search_service import RoomSearchService
from app.utils.response import success_response, error_response, paginated_response
from app.utils.decorators import authenticated_required, landlord_required, tenant_required
from app.extensions import db
from app.models.room import Room, Building

rooms_bp = Blueprint("rooms", __name__, url_prefix="/api/v1/rooms")


@rooms_bp.get("/search")
def search_rooms():
    """
    GET /api/v1/rooms/search
    Tìm kiếm phòng trống theo bộ lọc (public, không cần JWT).
    Query params: min_price, max_price, min_area, max_area, floor,
                  has_balcony, has_washing_machine, has_kitchen, has_parking,
                  page, per_page
    """
    try:
        page = max(1, int(request.args.get("page", 1)))
        per_page = min(50, max(1, int(request.args.get("per_page", 20))))

        def optional_float(key):
            val = request.args.get(key)
            return float(val) if val is not None and val != "" else None

        def optional_int(key):
            val = request.args.get(key)
            return int(val) if val is not None and val != "" else None

        def optional_bool(key):
            val = request.args.get(key, "").lower()
            if val == "true":
                return True
            if val == "false":
                return False
            return None

    except (ValueError, TypeError):
        return error_response("INVALID_QUERY_PARAMS", "Tham số tìm kiếm không hợp lệ.", 400)

    rooms, total = RoomSearchService.search_vacant_rooms(
        min_price=optional_float("min_price"),
        max_price=optional_float("max_price"),
        min_area=optional_float("min_area"),
        max_area=optional_float("max_area"),
        floor=optional_int("floor"),
        has_balcony=optional_bool("has_balcony"),
        has_washing_machine=optional_bool("has_washing_machine"),
        has_kitchen=optional_bool("has_kitchen"),
        has_parking=optional_bool("has_parking"),
        page=page,
        per_page=per_page,
    )

    return paginated_response(rooms, page, per_page, total)


@rooms_bp.get("/my-room")
@tenant_required
def get_my_room():
    """
    GET /api/v1/rooms/my-room
    Khách thuê xem thông tin phòng và hợp đồng đang ở.
    Yêu cầu JWT với role: tenant hoặc landlord/admin.
    """
    user_id = int(get_jwt_identity())
    room_info = RoomSearchService.get_room_with_active_contract(user_id)

    if not room_info:
        return error_response(
            "NO_ACTIVE_ROOM",
            "Bạn hiện chưa có phòng đang thuê hoặc hợp đồng đã hết hạn.",
            404,
        )

    return success_response(room_info)


@rooms_bp.get("/<int:room_id>")
@authenticated_required
def get_room_detail(room_id: int):
    """
    GET /api/v1/rooms/:id
    Lấy chi tiết một phòng. Yêu cầu JWT.
    """
    room = db.session.get(Room, room_id)
    if not room:
        return error_response("ROOM_NOT_FOUND", f"Phòng #{room_id} không tồn tại.", 404)

    return success_response(room.to_dict(include_building=True))


@rooms_bp.get("")
@landlord_required
def list_all_rooms():
    """
    GET /api/v1/rooms
    Landlord/Admin lấy danh sách tất cả phòng với bộ lọc.
    Yêu cầu JWT với role: landlord hoặc admin.
    Query params: status, building_id, page, per_page
    """
    try:
        page = max(1, int(request.args.get("page", 1)))
        per_page = min(100, max(1, int(request.args.get("per_page", 20))))
        status = request.args.get("status")
        building_id = request.args.get("building_id")
        building_id = int(building_id) if building_id else None
    except (ValueError, TypeError):
        return error_response("INVALID_QUERY_PARAMS", "Tham số không hợp lệ.", 400)

    query = db.session.query(Room).join(Building)

    if status:
        query = query.filter(Room.status == status)
    if building_id:
        query = query.filter(Room.building_id == building_id)

    query = query.order_by(Building.name.asc(), Room.room_number.asc())

    total = query.count()
    rooms = query.offset((page - 1) * per_page).limit(per_page).all()

    return paginated_response(
        [r.to_dict(include_building=True) for r in rooms],
        page, per_page, total,
    )
