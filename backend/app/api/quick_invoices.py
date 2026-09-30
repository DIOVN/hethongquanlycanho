"""
SAMS - Quick Invoicing Controller
Endpoint tạo hóa đơn nhanh tại chỗ cho Chủ nhà / Quản lý khi kiểm tra phòng.
Tuân thủ API.md Section 3.5 và FR-LANDLORD-07.
"""
from datetime import datetime, timezone
from flask import Blueprint, request

from app.utils.response import success_response, error_response
from app.utils.decorators import landlord_required
from app.utils.upload import save_uploaded_file
from app.services.billing_service import BillingService
from app.services.gemini_vision_service import GeminiVisionService

quick_invoices_bp = Blueprint("quick_invoices", __name__, url_prefix="/api/v1/quick-invoices")


@quick_invoices_bp.post("")
@landlord_required
def create_quick_invoice():
    """
    Tạo hóa đơn nhanh tại chỗ từ ảnh chụp công tơ và chỉ số.
    Hỗ trợ upload ảnh trực tiếp từ camera điện thoại của chủ nhà.
    """
    now = datetime.now(timezone.utc)
    room_id_raw = request.form.get("room_id")
    month_raw = request.form.get("month", str(now.month))
    year_raw = request.form.get("year", str(now.year))

    if not room_id_raw:
        return error_response("MISSING_ROOM_ID", "room_id là bắt buộc.", 400)

    try:
        room_id = int(room_id_raw)
        month = int(month_raw)
        year = int(year_raw)
    except ValueError:
        return error_response("INVALID_DATA", "room_id, month, year phải là số nguyên hợp lệ.", 422)

    if not (1 <= month <= 12):
        return error_response("INVALID_MONTH", "Tháng phải từ 1 đến 12.", 422)

    # 1. Xử lý ảnh và chỉ số công tơ điện
    elec_image_url = None
    elec_reading = None
    elec_conf = None

    if "electricity_reading" in request.form and request.form["electricity_reading"].strip():
        try:
            elec_reading = float(request.form["electricity_reading"])
        except ValueError:
            return error_response("INVALID_READING", "Chỉ số điện không hợp lệ.", 422)

    if "electricity_image" in request.files and request.files["electricity_image"].filename:
        img_file = request.files["electricity_image"]
        img_bytes = img_file.read()
        img_file.seek(0)
        try:
            elec_image_url = save_uploaded_file(img_file, subfolder="meters")
        except Exception as e:
            return error_response("UPLOAD_FAILED", f"Lỗi lưu ảnh đồng hồ điện: {str(e)}", 400)

        # Nếu chưa có chỉ số điện nhập tay, OCR từ ảnh
        if elec_reading is None:
            ocr = GeminiVisionService.scan_meter_image(img_bytes, meter_type="electricity")
            elec_reading = ocr.get("reading")
            elec_conf = ocr.get("confidence")

    # 2. Xử lý ảnh và chỉ số công tơ nước
    water_image_url = None
    water_reading = None
    water_conf = None

    if "water_reading" in request.form and request.form["water_reading"].strip():
        try:
            water_reading = float(request.form["water_reading"])
        except ValueError:
            return error_response("INVALID_READING", "Chỉ số nước không hợp lệ.", 422)

    if "water_image" in request.files and request.files["water_image"].filename:
        img_file = request.files["water_image"]
        img_bytes = img_file.read()
        img_file.seek(0)
        try:
            water_image_url = save_uploaded_file(img_file, subfolder="meters")
        except Exception as e:
            return error_response("UPLOAD_FAILED", f"Lỗi lưu ảnh đồng hồ nước: {str(e)}", 400)

        # Nếu chưa có chỉ số nước nhập tay, OCR từ ảnh
        if water_reading is None:
            ocr = GeminiVisionService.scan_meter_image(img_bytes, meter_type="water")
            water_reading = ocr.get("reading")
            water_conf = ocr.get("confidence")

    # 3. Tạo hóa đơn qua BillingService
    try:
        invoice_data = BillingService.create_quick_invoice(
            room_id=room_id,
            month=month,
            year=year,
            electricity_reading=elec_reading,
            water_reading=water_reading,
            electricity_image_url=elec_image_url,
            water_image_url=water_image_url,
            electricity_confidence=elec_conf,
            water_confidence=water_conf,
        )
    except ValueError as ve:
        return error_response("QUICK_INVOICE_FAILED", str(ve), 400)
    except Exception as e:
        return error_response("INTERNAL_ERROR", f"Lỗi lập hóa đơn: {str(e)}", 500)

    return success_response(data=invoice_data, status_code=201)
