"""
SAMS - Service Tickets Controller
Tiếp nhận và theo dõi tiến độ xử lý báo hỏng, sự cố kỹ thuật căn hộ.
"""
from datetime import datetime, timezone
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, get_jwt

from app.extensions import db
from app.models.expense import ServiceTicket
from app.models.room import Room
from app.models.contract import Contract
from app.utils.response import success_response, error_response
from app.utils.decorators import authenticated_required, landlord_required
from app.utils.upload import save_uploaded_file

tickets_bp = Blueprint("tickets", __name__, url_prefix="/api/v1/tickets")


@tickets_bp.get("")
@authenticated_required
def get_tickets():
    """Lấy danh sách các yêu cầu sửa chữa/báo hỏng."""
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get("role", "")

    query = db.session.query(ServiceTicket)

    # Nếu là khách thuê, chỉ xem ticket của phòng mình
    if role == "tenant":
        query = query.filter(ServiceTicket.tenant_id == user_id)
    else:
        room_id = request.args.get("room_id", type=int)
        status = request.args.get("status")
        if room_id:
            query = query.filter(ServiceTicket.room_id == room_id)
        if status:
            query = query.filter(ServiceTicket.status == status)

    tickets = query.order_by(ServiceTicket.created_at.desc()).all()
    results = []
    for t in tickets:
        data = t.to_dict()
        if t.room:
            data["room_number"] = t.room.room_number
        results.append(data)
    return success_response(data=results)


@tickets_bp.post("")
@authenticated_required
def create_ticket():
    """Khách thuê gửi yêu cầu sửa chữa / báo hỏng."""
    user_id = int(get_jwt_identity())

    # Hỗ trợ cả form-data (upload ảnh hư hỏng) lẫn json
    if request.content_type and "multipart/form-data" in request.content_type:
        room_id_raw = request.form.get("room_id")
        category = request.form.get("category", "repair")
        title = request.form.get("title")
        description = request.form.get("description")
        priority = request.form.get("priority", "medium")
        image_url = None
        if "image" in request.files and request.files["image"].filename:
            try:
                image_url = save_uploaded_file(request.files["image"], subfolder="tickets")
            except Exception as e:
                return error_response("UPLOAD_FAILED", f"Lỗi upload ảnh: {str(e)}", 400)
    else:
        payload = request.get_json(silent=True) or {}
        room_id_raw = payload.get("room_id")
        category = payload.get("category", "repair")
        title = payload.get("title")
        description = payload.get("description")
        priority = payload.get("priority", "medium")
        image_url = payload.get("image_url")

    if not title:
        return error_response("MISSING_TITLE", "Tiêu đề yêu cầu sửa chữa không được rỗng.", 400)

    # Xác định phòng
    room_id = None
    if room_id_raw:
        try:
            room_id = int(room_id_raw)
        except ValueError:
            pass
    if not room_id:
        contract = (
            db.session.query(Contract)
            .filter(Contract.tenant_id == user_id, Contract.status == "active")
            .first()
        )
        if contract:
            room_id = contract.room_id
        else:
            room = db.session.query(Room).filter(Room.current_tenant_id == user_id).first()
            if room:
                room_id = room.id

    if not room_id:
        return error_response("ROOM_NOT_FOUND", "Vui lòng chọn phòng cần sửa chữa.", 400)

    ticket = ServiceTicket(
        room_id=room_id,
        tenant_id=user_id,
        category=category,
        title=title.strip(),
        description=description.strip() if description else None,
        image_url=image_url,
        priority=priority,
        status="pending",
    )
    db.session.add(ticket)
    db.session.commit()

    res = ticket.to_dict()
    if ticket.room:
        res["room_number"] = ticket.room.room_number
    return success_response(data=res, status_code=201)


@tickets_bp.put("/<int:ticket_id>/status")
@landlord_required
def update_ticket_status(ticket_id: int):
    """Chủ nhà/Admin cập nhật trạng thái xử lý ticket (in_progress, resolved, cancelled)."""
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return error_response("NOT_FOUND", "Không tìm thấy yêu cầu sửa chữa.", 404)

    payload = request.get_json(silent=True) or {}
    new_status = payload.get("status")
    repair_cost = payload.get("repair_cost")

    if new_status:
        ticket.status = new_status
    if repair_cost is not None:
        try:
            ticket.repair_cost = float(repair_cost)
        except ValueError:
            pass

    db.session.commit()
    res = ticket.to_dict()
    if ticket.room:
        res["room_number"] = ticket.room.room_number
    return success_response(data=res)
