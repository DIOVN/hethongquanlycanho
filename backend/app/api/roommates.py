"""
SAMS - Roommates API Controller
Endpoints quản lý nhân khẩu trong phòng.
GET  /api/v1/rooms/:room_id/roommates
POST /api/v1/rooms/:room_id/roommates
PATCH /api/v1/roommates/:id/status
Tuân thủ API.md §3.6
"""
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, get_jwt

from app.services.roommate_service import RoommateService
from app.utils.response import success_response, error_response
from app.utils.decorators import authenticated_required, landlord_required

roommates_bp = Blueprint("roommates", __name__)


@roommates_bp.get("/api/v1/rooms/<int:room_id>/roommates")
@authenticated_required
def list_roommates(room_id: int):
    """
    GET /api/v1/rooms/:room_id/roommates
    Lấy danh sách người ở cùng trong phòng.
    - Khách thuê chỉ xem được phòng của mình.
    - Landlord/Admin xem được mọi phòng.
    """
    claims = get_jwt()
    user_id = int(get_jwt_identity())
    role = claims.get("role", "")

    # Nếu là tenant: chỉ được xem phòng của chính mình
    if role == "tenant":
        room_info = __get_tenant_room_id(user_id)
        if room_info != room_id:
            return error_response(
                "FORBIDDEN",
                "Bạn không có quyền xem nhân khẩu của phòng này.",
                403,
            )

    roommates = RoommateService.get_room_occupants(room_id)
    return success_response(roommates)


@roommates_bp.post("/api/v1/rooms/<int:room_id>/roommates")
@authenticated_required
def add_roommate(room_id: int):
    """
    POST /api/v1/rooms/:room_id/roommates
    Thêm người ở cùng vào phòng.
    - Tenant: chỉ thêm vào phòng mình đang ở.
    - Landlord/Admin: thêm vào bất kỳ phòng nào.
    """
    claims = get_jwt()
    user_id = int(get_jwt_identity())
    role = claims.get("role", "")

    # Kiểm tra quyền cho tenant
    if role == "tenant":
        tenant_room = __get_tenant_room_id(user_id)
        if tenant_room != room_id:
            return error_response(
                "FORBIDDEN",
                "Bạn chỉ có thể đăng ký nhân khẩu cho phòng của mình.",
                403,
            )

    data = request.get_json(silent=True)
    if not data:
        return error_response("INVALID_JSON", "Request body phải là JSON hợp lệ.", 400)

    full_name = data.get("full_name", "").strip()
    if not full_name:
        return error_response("MISSING_FULL_NAME", "Họ và tên người cư trú là bắt buộc.", 422)

    roommate, error_code = RoommateService.register_occupant(
        room_id=room_id,
        full_name=full_name,
        phone=data.get("phone"),
        cccd_number=data.get("cccd_number"),
        date_of_birth=data.get("date_of_birth"),
        gender=data.get("gender"),
        hometown=data.get("hometown"),
        vehicle_plate=data.get("vehicle_plate"),
        is_primary_tenant=data.get("is_primary_tenant", False),
    )

    if error_code:
        messages = {
            "ROOM_NOT_FOUND": "Phòng không tồn tại.",
            "INVALID_CCCD_FORMAT": "CCCD phải gồm đúng 12 chữ số.",
            "CCCD_ALREADY_REGISTERED": "CCCD này đã được đăng ký trong phòng.",
            "INVALID_DATE_FORMAT": "Ngày sinh không hợp lệ (định dạng YYYY-MM-DD).",
        }
        status = 404 if error_code == "ROOM_NOT_FOUND" else 422
        return error_response(error_code, messages.get(error_code, "Lỗi không xác định."), status)

    return success_response(roommate.to_dict(), status_code=201)


@roommates_bp.patch("/api/v1/roommates/<int:roommate_id>/status")
@landlord_required
def update_residence_status(roommate_id: int):
    """
    PATCH /api/v1/roommates/:id/status
    Cập nhật trạng thái đăng ký tạm trú (chỉ landlord/admin).
    Body: { "status": "registered" | "rejected" | "pending" }
    """
    data = request.get_json(silent=True)
    if not data or "status" not in data:
        return error_response("MISSING_STATUS", "Trường 'status' là bắt buộc.", 422)

    roommate, error_code = RoommateService.update_residence_status(
        roommate_id=roommate_id,
        new_status=data["status"],
    )

    if error_code:
        messages = {
            "INVALID_STATUS": "Trạng thái không hợp lệ. Chấp nhận: pending | registered | rejected.",
            "ROOMMATE_NOT_FOUND": "Người cư trú không tồn tại.",
        }
        status = 404 if error_code == "ROOMMATE_NOT_FOUND" else 422
        return error_response(error_code, messages.get(error_code, "Lỗi không xác định."), status)

    return success_response(roommate.to_dict())


def __get_tenant_room_id(user_id: int) -> int | None:
    """Lấy room_id đang thuê của tenant hiện tại."""
    from app.models.contract import Contract
    from app.extensions import db

    contract = (
        db.session.query(Contract)
        .filter(
            Contract.tenant_id == user_id,
            Contract.status == "active",
        )
        .first()
    )
    return contract.room_id if contract else None
