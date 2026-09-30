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


@rooms_bp.get("/buildings")
@authenticated_required
def list_buildings():
    """
    GET /api/v1/rooms/buildings
    Lấy danh sách các tòa nhà căn hộ đang quản lý.
    """
    buildings = Building.query.order_by(Building.name.asc()).all()
    return success_response([b.to_dict() for b in buildings])


@rooms_bp.post("")
@landlord_required
def create_room():
    """
    POST /api/v1/rooms
    Tạo phòng trọ / căn hộ mới.
    """
    data = request.get_json(silent=True) or {}
    room_number = str(data.get("room_number", "")).strip()
    building_id = data.get("building_id")
    base_price = data.get("base_price")

    if not room_number:
        return error_response("MISSING_ROOM_NUMBER", "Số phòng là bắt buộc.", 422)
    if not building_id:
        return error_response("MISSING_BUILDING_ID", "Tòa nhà là bắt buộc.", 422)
    if base_price is None or float(base_price) <= 0:
        return error_response("INVALID_BASE_PRICE", "Giá phòng cơ bản phải lớn hơn 0.", 422)

    building = db.session.get(Building, int(building_id))
    if not building:
        return error_response("BUILDING_NOT_FOUND", "Tòa nhà không tồn tại.", 404)

    # Kiểm tra trùng số phòng trong cùng tòa nhà
    existing = Room.query.filter_by(building_id=building.id, room_number=room_number).first()
    if existing:
        return error_response("ROOM_ALREADY_EXISTS", f"Phòng {room_number} đã tồn tại trong {building.name}.", 409)

    new_room = Room(
        building_id=building.id,
        room_number=room_number,
        floor=int(data.get("floor", 1)) if data.get("floor") else None,
        base_price=float(base_price),
        area_sqm=float(data.get("area_sqm", 25.0)) if data.get("area_sqm") else None,
        status=data.get("status", "vacant"),
        has_balcony=bool(data.get("has_balcony", False)),
        has_washing_machine=bool(data.get("has_washing_machine", False)),
        has_kitchen=bool(data.get("has_kitchen", False)),
        has_parking=bool(data.get("has_parking", False)),
        description=data.get("description", ""),
    )

    db.session.add(new_room)
    db.session.commit()

    return success_response(new_room.to_dict(include_building=True), message="Tạo phòng thành công!", status_code=201)


@rooms_bp.put("/<int:room_id>")
@landlord_required
def update_room(room_id: int):
    """
    PUT /api/v1/rooms/:room_id
    Cập nhật toàn diện thông tin phòng.
    """
    room = db.session.get(Room, room_id)
    if not room:
        return error_response("ROOM_NOT_FOUND", f"Phòng #{room_id} không tồn tại.", 404)

    data = request.get_json(silent=True) or {}
    if "room_number" in data:
        room.room_number = str(data["room_number"]).strip()
    if "floor" in data and data["floor"] is not None:
        room.floor = int(data["floor"])
    if "base_price" in data and data["base_price"] is not None:
        room.base_price = float(data["base_price"])
    if "area_sqm" in data and data["area_sqm"] is not None:
        room.area_sqm = float(data["area_sqm"])
    if "status" in data and data["status"] in ["vacant", "occupied", "maintenance"]:
        room.status = data["status"]
    if "has_balcony" in data:
        room.has_balcony = bool(data["has_balcony"])
    if "has_washing_machine" in data:
        room.has_washing_machine = bool(data["has_washing_machine"])
    if "has_kitchen" in data:
        room.has_kitchen = bool(data["has_kitchen"])
    if "has_parking" in data:
        room.has_parking = bool(data["has_parking"])
    if "description" in data:
        room.description = data["description"]
    if "current_tenant_id" in data:
        room.current_tenant_id = int(data["current_tenant_id"]) if data["current_tenant_id"] else None

    db.session.commit()
    return success_response(room.to_dict(include_building=True), message="Cập nhật phòng thành công!")


@rooms_bp.patch("/<int:room_id>/status")
@landlord_required
def patch_room_status(room_id: int):
    """
    PATCH /api/v1/rooms/:room_id/status
    Đổi nhanh trạng thái phòng (vacant, occupied, maintenance).
    """
    room = db.session.get(Room, room_id)
    if not room:
        return error_response("ROOM_NOT_FOUND", f"Phòng #{room_id} không tồn tại.", 404)

    data = request.get_json(silent=True) or {}
    new_status = data.get("status")
    if new_status not in ["vacant", "occupied", "maintenance"]:
        return error_response("INVALID_STATUS", "Trạng thái hợp lệ: vacant, occupied, maintenance.", 400)

    room.status = new_status
    db.session.commit()
    return success_response(room.to_dict(include_building=True), message=f"Đã chuyển trạng thái sang {new_status}!")
