"""
SAMS - Meter Readings & AI OCR Controller
Endpoint quét ảnh công tơ điện nước qua Gemini Vision và ghi nhận chỉ số.
Tuân thủ API.md Section 3.4.
"""
from datetime import datetime, timezone
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity

from app.utils.response import success_response, error_response
from app.utils.decorators import authenticated_required
from app.utils.upload import save_uploaded_file
from app.services.gemini_vision_service import GeminiVisionService
from app.services.billing_service import BillingService

meters_bp = Blueprint("meters", __name__, url_prefix="/api/v1/meters")


@meters_bp.post("/scan-reading")
@authenticated_required
def scan_meter_reading():
    """
    Tải ảnh chụp công tơ điện hoặc nước lên để Gemini Flash Vision OCR đọc số.
    Form Data:
        image: File ảnh chụp công tơ
        meter_type: 'electricity' | 'water'
        room_id: integer
    """
    if "image" not in request.files:
        return error_response("MISSING_FILE", "Vui lòng đính kèm file ảnh công tơ.", 400)

    image_file = request.files["image"]
    meter_type = request.form.get("meter_type", "electricity").lower()
    room_id_raw = request.form.get("room_id")

    if not room_id_raw:
        return error_response("MISSING_ROOM_ID", "Vui lòng cung cấp mã phòng (room_id).", 400)

    try:
        room_id = int(room_id_raw)
    except ValueError:
        return error_response("INVALID_ROOM_ID", "room_id phải là số nguyên.", 422)

    if meter_type not in ("electricity", "water"):
        return error_response("INVALID_METER_TYPE", "meter_type phải là 'electricity' hoặc 'water'.", 422)

    # Đọc bytes để gửi sang Gemini Vision
    image_bytes = image_file.read()
    image_file.seek(0)

    # Lưu ảnh vào thư mục uploads/meters
    try:
        saved_image_url = save_uploaded_file(image_file, subfolder="meters")
    except Exception as e:
        return error_response("UPLOAD_FAILED", f"Lỗi lưu trữ ảnh: {str(e)}", 400)

    # Gọi AI OCR
    ocr_result = GeminiVisionService.scan_meter_image(image_bytes, meter_type=meter_type)
    detected_val = float(ocr_result.get("reading", 0.0))
    confidence_val = float(ocr_result.get("confidence", 0.0))

    # Lấy chỉ số tháng trước để đối chiếu
    now = datetime.now(timezone.utc)
    prev_reading = BillingService.get_latest_meter_reading(room_id, meter_type, before_month=now.month, before_year=now.year)
    prev_val = float(prev_reading.reading_value) if prev_reading and prev_reading.reading_value is not None else 0.0

    warning_flag = None
    if detected_val < prev_val:
        warning_flag = "READING_LOWER_THAN_PREVIOUS"

    consumption = max(0.0, detected_val - prev_val) if not warning_flag else 0.0

    return success_response(
        data={
            "detected_reading": detected_val,
            "confidence": confidence_val,
            "meter_type": meter_type,
            "previous_reading": prev_val,
            "consumption": consumption,
            "temporary_image_url": saved_image_url,
            "warning_flag": warning_flag,
        },
        meta={"timestamp": now.isoformat()},
    )


@meters_bp.post("/confirm-reading")
@authenticated_required
def confirm_meter_reading():
    """
    Xác nhận lưu chỉ số công tơ chính thức vào CSDL sau khi người dùng kiểm tra kết quả OCR.
    JSON Body:
        room_id: integer
        meter_type: 'electricity' | 'water'
        confirmed_reading: float
        image_url: string (tùy chọn)
        ai_confidence: float (tùy chọn)
        month: integer (tùy chọn)
        year: integer (tùy chọn)
    """
    payload = request.get_json(silent=True) or {}
    room_id = payload.get("room_id")
    meter_type = payload.get("meter_type", "electricity")
    confirmed_val = payload.get("confirmed_reading")

    if not room_id or confirmed_val is None:
        return error_response(
            "MISSING_PARAMETERS",
            "Thiếu các trường bắt buộc: room_id, confirmed_reading.",
            400,
        )

    now = datetime.now(timezone.utc)
    month = int(payload.get("month", now.month))
    year = int(payload.get("year", now.year))

    try:
        reading = BillingService.record_utility_reading(
            room_id=int(room_id),
            meter_type=str(meter_type),
            reading_value=float(confirmed_val),
            month=month,
            year=year,
            image_proof_url=payload.get("image_url"),
            ai_confidence=payload.get("ai_confidence"),
        )
    except Exception as e:
        return error_response("RECORDING_FAILED", f"Lỗi ghi nhận chỉ số: {str(e)}", 400)

    return success_response(
        data={
            "reading_id": reading.id,
            "room_id": reading.room_id,
            "meter_type": reading.meter_type,
            "reading_value": float(reading.reading_value),
            "consumption": float(reading.consumption or 0),
            "month": reading.month,
            "year": reading.year,
            "recorded_at": reading.recorded_at.isoformat() if reading.recorded_at else None,
        },
        status_code=201,
    )
