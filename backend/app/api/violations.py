"""
SAMS - Violations Controller
Quản lý biên bản cảnh cáo, xử lý vi phạm nội quy tòa nhà 3 cấp độ.
Tuân thủ API.md Section 3.6 và FR-LANDLORD-08.
"""
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, get_jwt

from app.utils.response import success_response, error_response
from app.utils.decorators import authenticated_required, landlord_required
from app.utils.upload import save_uploaded_file
from app.services.violation_service import ViolationService
from app.models.room import Room
from app.models.contract import Contract
from app.extensions import db

violations_bp = Blueprint("violations", __name__, url_prefix="/api/v1/violations")


@violations_bp.get("")
@authenticated_required
def get_violations():
    """
    Danh sách các biên bản vi phạm nội quy.
    - Tenant: Chỉ xem các biên bản của phòng mình.
    - Landlord/Admin: Xem toàn bộ tòa nhà hoặc lọc theo room_id/status.
    """
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get("role", "")

    req_room_id = request.args.get("room_id", type=int)
    status = request.args.get("status")
    severity = request.args.get("severity")

    if role == "tenant":
        # Xác định phòng của khách thuê
        contract = (
            db.session.query(Contract)
            .filter(Contract.tenant_id == user_id, Contract.status == "active")
            .first()
        )
        if not contract:
            room = db.session.query(Room).filter(Room.current_tenant_id == user_id).first()
            user_room_id = room.id if room else None
        else:
            user_room_id = contract.room_id

        if not user_room_id:
            return success_response(data=[])
        req_room_id = user_room_id

    violations = ViolationService.get_violations(
        room_id=req_room_id,
        status=status,
        severity=severity,
    )
    return success_response(data=violations)


@violations_bp.post("")
@landlord_required
def create_violation():
    """
    Chủ nhà lập biên bản cảnh cáo hoặc phạt tiền phòng vi phạm nội quy.
    Hỗ trợ cả JSON body lẫn Multipart Form-Data (kèm ảnh bằng chứng).
    """
    user_id = int(get_jwt_identity())

    # Kiểm tra multipart hay json
    if request.content_type and "multipart/form-data" in request.content_type:
        room_id_raw = request.form.get("room_id")
        violation_type = request.form.get("violation_type")
        severity = request.form.get("severity", "reminder")
        title = request.form.get("title")
        description = request.form.get("description")
        penalty_amount = request.form.get("penalty_amount")
        evidence_image_url = None

        if "evidence_image" in request.files and request.files["evidence_image"].filename:
            try:
                evidence_image_url = save_uploaded_file(request.files["evidence_image"], subfolder="violations")
            except Exception as e:
                return error_response("UPLOAD_FAILED", f"Lỗi lưu ảnh bằng chứng: {str(e)}", 400)
    else:
        payload = request.get_json(silent=True) or {}
        room_id_raw = payload.get("room_id")
        violation_type = payload.get("violation_type")
        severity = payload.get("severity", "reminder")
        title = payload.get("title")
        description = payload.get("description")
        penalty_amount = payload.get("penalty_amount")
        evidence_image_url = payload.get("evidence_image_url")

    if not room_id_raw or not violation_type or not title:
        return error_response(
            "MISSING_FIELDS",
            "Các trường room_id, violation_type, title là bắt buộc.",
            400,
        )

    try:
        room_id = int(room_id_raw)
    except ValueError:
        return error_response("INVALID_ROOM_ID", "room_id phải là số nguyên.", 422)

    try:
        violation = ViolationService.report_violation(
            room_id=room_id,
            violation_type=violation_type,
            severity=severity,
            title=title,
            description=description,
            reported_by=user_id,
            evidence_image_url=evidence_image_url,
            penalty_amount=penalty_amount,
        )
    except ValueError as ve:
        return error_response("VIOLATION_CREATION_FAILED", str(ve), 400)
    except Exception as e:
        return error_response("INTERNAL_ERROR", f"Lỗi hệ thống: {str(e)}", 500)

    return success_response(
        data={
            "violation_id": violation["id"],
            "room_id": violation["room_id"],
            "severity": violation["severity"],
            "penalty_amount": violation["penalty_amount"],
            "status": violation["status"],
            "created_at": violation["created_at"],
        },
        status_code=201,
    )


@violations_bp.get("/<int:violation_id>")
@authenticated_required
def get_violation_detail(violation_id: int):
    """Lấy chi tiết biên bản vi phạm theo ID."""
    violation = ViolationService.get_violation_by_id(violation_id)
    if not violation:
        return error_response("NOT_FOUND", "Không tìm thấy biên bản vi phạm.", 404)
    return success_response(data=violation)


@violations_bp.put("/<int:violation_id>/acknowledge")
@authenticated_required
def acknowledge_violation(violation_id: int):
    """Khách thuê xác nhận đã đọc thông báo nhắc nhở/cảnh cáo vi phạm."""
    try:
        updated = ViolationService.acknowledge_violation(violation_id)
    except ValueError as ve:
        return error_response("NOT_FOUND", str(ve), 404)

    return success_response(data={
        "violation_id": updated["id"],
        "status": updated["status"],
        "acknowledged_at": updated.get("created_at"),
    })


@violations_bp.put("/<int:violation_id>/resolve")
@landlord_required
def resolve_violation(violation_id: int):
    """Chủ nhà/Admin đóng biên bản vi phạm khi đã giải quyết xong."""
    try:
        updated = ViolationService.resolve_violation(violation_id)
    except ValueError as ve:
        return error_response("NOT_FOUND", str(ve), 404)

    return success_response(data=updated)
