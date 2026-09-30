"""
SAMS - Billing & Payment Hub Controller
Quản lý danh sách hóa đơn, tải ảnh ủy nhiệm chi và xác nhận thanh toán.
Tuân thủ API.md Section 3.5 và FR-TENANT-06.
"""
from datetime import datetime, timezone
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, get_jwt

from app.utils.response import success_response, error_response
from app.utils.decorators import authenticated_required, landlord_required
from app.utils.upload import save_uploaded_file
from app.services.billing_service import BillingService
from app.models.room import Room
from app.models.contract import Contract
from app.extensions import db

billing_bp = Blueprint("billing", __name__, url_prefix="/api/v1/billing")


@billing_bp.get("/my-invoices")
@authenticated_required
def get_my_invoices():
    """Lấy danh sách các hóa đơn của khách thuê đang đăng nhập."""
    user_id = int(get_jwt_identity())

    # Tìm phòng của khách thuê
    contract = (
        db.session.query(Contract)
        .filter(Contract.tenant_id == user_id, Contract.status == "active")
        .first()
    )
    room_id = None
    if contract:
        room_id = contract.room_id
    else:
        room = db.session.query(Room).filter(Room.current_tenant_id == user_id).first()
        if room:
            room_id = room.id

    if not room_id:
        return success_response(data=[])

    invoices = BillingService.get_invoices(room_id=room_id)
    return success_response(data=invoices)


@billing_bp.get("/invoices")
@landlord_required
def get_all_invoices():
    """Chủ nhà/Admin xem danh sách tất cả hóa đơn theo bộ lọc."""
    room_id = request.args.get("room_id", type=int)
    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)
    status = request.args.get("status")

    invoices = BillingService.get_invoices(
        room_id=room_id,
        month=month,
        year=year,
        status=status,
    )
    return success_response(data=invoices)


@billing_bp.get("/invoices/<int:invoice_id>")
@authenticated_required
def get_invoice_detail(invoice_id: int):
    """Lấy thông tin chi tiết một hóa đơn kèm các khoản mục chi tiết."""
    invoice_data = BillingService.get_invoice_by_id(invoice_id)
    if not invoice_data:
        return error_response("NOT_FOUND", "Không tìm thấy hóa đơn.", 404)

    # Nếu là tenant, chỉ cho xem hóa đơn của phòng mình
    claims = get_jwt()
    role = claims.get("role", "")
    user_id = int(get_jwt_identity())
    if role == "tenant":
        room = db.session.get(Room, invoice_data["room_id"])
        if not room or (room.current_tenant_id != user_id):
            return error_response("FORBIDDEN", "Bạn không có quyền xem hóa đơn của phòng khác.", 403)

    return success_response(data=invoice_data)


@billing_bp.post("/<int:invoice_id>/payment-slip")
@authenticated_required
def upload_payment_slip(invoice_id: int):
    """
    Khách thuê tải ảnh chụp màn hình biên lai chuyển khoản ngân hàng.
    Form-data:
        slip_image: File ảnh biên lai
    """
    if "slip_image" not in request.files:
        return error_response("MISSING_FILE", "Vui lòng chọn ảnh chụp biên lai chuyển khoản.", 400)

    slip_file = request.files["slip_image"]
    try:
        saved_slip_url = save_uploaded_file(slip_file, subfolder="slips")
    except Exception as e:
        return error_response("UPLOAD_FAILED", f"Lỗi lưu trữ ảnh biên lai: {str(e)}", 400)

    try:
        result = BillingService.upload_payment_slip(invoice_id, saved_slip_url)
    except ValueError as ve:
        return error_response("NOT_FOUND", str(ve), 404)

    return success_response(data=result)


@billing_bp.post("/invoices/<int:invoice_id>/confirm-payment")
@landlord_required
def confirm_invoice_payment(invoice_id: int):
    """Chủ nhà/Admin xác nhận đối soát biên lai thành công và đánh dấu đã thanh toán."""
    try:
        updated_invoice = BillingService.confirm_payment(invoice_id)
    except ValueError as ve:
        return error_response("NOT_FOUND", str(ve), 404)

    return success_response(data=updated_invoice)


@billing_bp.post("/generate")
@landlord_required
def generate_batch_invoices():
    """
    Tự động tính tiền và phát hành hóa đơn hàng loạt cho tất cả các phòng đang có khách thuê.
    JSON Body:
        month: integer (1-12)
        year: integer
    """
    payload = request.get_json(silent=True) or {}
    now = datetime.now(timezone.utc)
    month = int(payload.get("month", now.month))
    year = int(payload.get("year", now.year))

    # Lấy tất cả phòng occupied
    occupied_rooms = (
        db.session.query(Room)
        .filter(Room.status.in_(["occupied", "rented"]))
        .all()
    )

    created_invoices = []
    errors = []

    for r in occupied_rooms:
        try:
            inv = BillingService.create_quick_invoice(
                room_id=r.id,
                month=month,
                year=year,
            )
            created_invoices.append(inv)
        except Exception as e:
            errors.append({"room_id": r.id, "room_number": r.room_number, "error": str(e)})

    return success_response(
        data={
            "generated_count": len(created_invoices),
            "invoices": created_invoices,
            "errors": errors,
        },
        status_code=201,
    )
