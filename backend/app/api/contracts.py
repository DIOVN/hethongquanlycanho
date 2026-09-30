"""
SAMS - Contracts & Deposit Refund Controller
Quản lý vòng đời hợp đồng thuê phòng và nghiệm thu quyết toán hoàn trả tiền cọc.
"""
from datetime import datetime, date, timezone
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, get_jwt

from app.extensions import db
from app.models.contract import Contract
from app.models.room import Room
from app.services.refund_service import RefundService
from app.utils.response import success_response, error_response
from app.utils.decorators import authenticated_required, landlord_required

contracts_bp = Blueprint("contracts", __name__, url_prefix="/api/v1/contracts")


@contracts_bp.get("")
@authenticated_required
def get_contracts():
    """Lấy danh sách hợp đồng thuê."""
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get("role", "")

    query = db.session.query(Contract)
    if role == "tenant":
        query = query.filter(Contract.tenant_id == user_id)
    else:
        room_id = request.args.get("room_id", type=int)
        status = request.args.get("status")
        if room_id:
            query = query.filter(Contract.room_id == room_id)
        if status:
            query = query.filter(Contract.status == status)

    contracts = query.order_by(Contract.created_at.desc()).all()
    results = []
    for c in contracts:
        data = c.to_dict()
        if c.room:
            data["room_number"] = c.room.room_number
        if c.tenant:
            data["tenant_name"] = c.tenant.full_name or c.tenant.username
            data["tenant_phone"] = c.tenant.phone
        results.append(data)

    return success_response(data=results)


@contracts_bp.get("/<int:contract_id>")
@authenticated_required
def get_contract_detail(contract_id: int):
    """Xem thông tin chi tiết một hợp đồng."""
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get("role", "")

    contract = db.session.get(Contract, contract_id)
    if not contract:
        return error_response("NOT_FOUND", "Không tìm thấy hợp đồng.", 404)

    if role == "tenant" and contract.tenant_id != user_id:
        return error_response("FORBIDDEN", "Không có quyền truy cập hợp đồng này.", 403)

    data = contract.to_dict()
    if contract.room:
        data["room_number"] = contract.room.room_number
    if contract.tenant:
        data["tenant_name"] = contract.tenant.full_name or contract.tenant.username
        data["tenant_phone"] = contract.tenant.phone
    return success_response(data=data)


@contracts_bp.post("")
@landlord_required
def create_contract():
    """Tạo mới một hợp đồng cho thuê phòng."""
    payload = request.get_json(silent=True) or {}
    room_id = payload.get("room_id")
    tenant_id = payload.get("tenant_id")
    start_date_str = payload.get("start_date")
    end_date_str = payload.get("end_date")
    monthly_rent = payload.get("monthly_rent")
    deposit_amount = payload.get("deposit_amount")
    notes = payload.get("notes")

    if not room_id or not tenant_id or not start_date_str or not end_date_str:
        return error_response("MISSING_FIELDS", "room_id, tenant_id, start_date, end_date là bắt buộc.", 400)

    room = db.session.get(Room, room_id)
    if not room:
        return error_response("NOT_FOUND", "Phòng không tồn tại.", 404)

    try:
        s_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        e_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except ValueError:
        return error_response("INVALID_DATE_FORMAT", "Định dạng ngày phải là YYYY-MM-DD.", 400)

    rent = float(monthly_rent) if monthly_rent is not None else float(room.base_price)
    deposit = float(deposit_amount) if deposit_amount is not None else rent * 2

    contract = Contract(
        room_id=room.id,
        tenant_id=int(tenant_id),
        start_date=s_date,
        end_date=e_date,
        monthly_rent=rent,
        deposit_amount=deposit,
        status="active",
        notes=notes,
    )
    # Cập nhật trạng thái phòng sang occupied
    room.status = "occupied"
    room.current_tenant_id = int(tenant_id)

    db.session.add(contract)
    db.session.commit()

    res = contract.to_dict()
    res["room_number"] = room.room_number
    return success_response(data=res, status_code=201)


@contracts_bp.get("/<int:contract_id>/refund-preview")
@landlord_required
def preview_refund(contract_id: int):
    """Tính toán bản dự toán quyết toán hoàn cọc khi trả phòng."""
    final_elec = request.args.get("final_electricity_reading", type=float)
    final_water = request.args.get("final_water_reading", type=float)

    try:
        preview = RefundService.preview_refund(
            contract_id=contract_id,
            final_electricity_reading=final_elec,
            final_water_reading=final_water,
        )
    except ValueError as ve:
        return error_response("PREVIEW_FAILED", str(ve), 400)
    except Exception as e:
        return error_response("INTERNAL_ERROR", f"Lỗi dự toán hoàn cọc: {str(e)}", 500)

    return success_response(data=preview)


@contracts_bp.post("/<int:contract_id>/settle-refund")
@landlord_required
def settle_refund(contract_id: int):
    """Nghiệm thu hoàn tất trả phòng, thanh lý hợp đồng và cấn trừ hoàn cọc."""
    payload = request.get_json(silent=True) or {}
    final_elec = payload.get("final_electricity_reading")
    final_water = payload.get("final_water_reading")
    deductions = payload.get("deductions", [])
    note = payload.get("note")

    try:
        settlement = RefundService.settle_refund(
            contract_id=contract_id,
            final_electricity_reading=float(final_elec) if final_elec is not None else None,
            final_water_reading=float(final_water) if final_water is not None else None,
            deductions=deductions,
            note=note,
        )
    except ValueError as ve:
        return error_response("SETTLEMENT_FAILED", str(ve), 400)
    except Exception as e:
        return error_response("INTERNAL_ERROR", f"Lỗi quyết toán trả phòng: {str(e)}", 500)

    return success_response(data=settlement)
