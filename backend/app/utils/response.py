"""
SAMS - Chuẩn hóa JSON Response Envelope
Mọi endpoint đều phải trả về định dạng này để Frontend xử lý nhất quán.
Cấu trúc: { success, data, meta, error }
"""
from datetime import datetime, timezone
from typing import Any
from flask import jsonify


def success_response(
    data: Any = None,
    status_code: int = 200,
    meta: dict | None = None,
    message: str | None = None,
) -> tuple:
    """
    Tạo JSON response thành công theo chuẩn SAMS Envelope.

    Args:
        data: Dữ liệu trả về (dict, list, hoặc None).
        status_code: HTTP status code (mặc định 200).
        meta: Metadata bổ sung (pagination, timestamp tùy chỉnh...).
        message: Thông điệp thành công tùy chọn.

    Returns:
        Tuple (Flask Response, HTTP status code).
    """
    response_meta = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if meta:
        response_meta.update(meta)
    if message:
        response_meta["message"] = message

    payload = {
        "success": True,
        "data": data,
        "meta": response_meta,
        "error": None,
    }
    return jsonify(payload), status_code


def error_response(
    error_code: str,
    message: str,
    status_code: int = 400,
    details: dict | None = None,
) -> tuple:
    """
    Tạo JSON response lỗi theo chuẩn SAMS Envelope.

    Args:
        error_code: Mã lỗi viết hoa, dùng underscore (VD: "INVALID_CREDENTIALS").
        message: Thông điệp lỗi thân thiện cho người dùng (tiếng Việt).
        status_code: HTTP status code (400, 401, 403, 404, 422, 500...).
        details: Chi tiết lỗi bổ sung (VD: danh sách field validation errors).

    Returns:
        Tuple (Flask Response, HTTP status code).
    """
    payload = {
        "success": False,
        "data": None,
        "meta": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        "error": {
            "code": error_code,
            "message": message,
            "details": details or {},
        },
    }
    return jsonify(payload), status_code


def paginated_response(
    data: list,
    page: int,
    per_page: int,
    total_items: int,
    status_code: int = 200,
) -> tuple:
    """
    Tạo JSON response phân trang cho danh sách kết quả.

    Args:
        data: Danh sách items trong trang hiện tại.
        page: Số trang hiện tại (bắt đầu từ 1).
        per_page: Số items mỗi trang.
        total_items: Tổng số items trong dataset.
        status_code: HTTP status code.

    Returns:
        Tuple (Flask Response, HTTP status code).
    """
    total_pages = max(1, (total_items + per_page - 1) // per_page)

    meta = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total_items": total_items,
            "total_pages": total_pages,
        },
    }

    payload = {
        "success": True,
        "data": data,
        "meta": meta,
        "error": None,
    }
    return jsonify(payload), status_code
