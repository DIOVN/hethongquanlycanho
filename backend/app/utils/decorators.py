"""
SAMS - Custom Decorators for Role-Based Access Control (RBAC)
Tuân thủ FR-AUTH-01: Phân quyền 3 cấp admin > landlord > tenant.
"""
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from app.utils.response import error_response


def _check_role(*required_roles: str):
    """
    Helper nội bộ: kiểm tra JWT token hợp lệ và role có trong danh sách cho phép.
    Sử dụng qua decorator factory pattern.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Bước 1: Xác thực JWT token
            try:
                verify_jwt_in_request()
            except Exception:
                return error_response(
                    error_code="UNAUTHORIZED",
                    message="Bạn chưa đăng nhập hoặc phiên đăng nhập đã hết hạn.",
                    status_code=401,
                )

            # Bước 2: Kiểm tra role
            claims = get_jwt()
            user_role = claims.get("role", "")

            # Admin luôn có quyền cao nhất - bypass mọi kiểm tra role khác
            if user_role == "admin" or user_role in required_roles:
                return fn(*args, **kwargs)

            return error_response(
                error_code="FORBIDDEN",
                message="Bạn không có quyền thực hiện thao tác này.",
                status_code=403,
            )
        return wrapper
    return decorator


def admin_required(fn):
    """Decorator: Chỉ cho phép role 'admin'."""
    return _check_role("admin")(fn)


def landlord_required(fn):
    """Decorator: Cho phép role 'admin' hoặc 'landlord'."""
    return _check_role("landlord")(fn)


def tenant_required(fn):
    """
    Decorator: Cho phép role 'tenant', 'landlord', 'admin'.
    Lưu ý: Chủ nhà (landlord) cũng có quyền xem dữ liệu tenant để quản lý.
    """
    return _check_role("tenant", "landlord")(fn)


def authenticated_required(fn):
    """Decorator: Yêu cầu đăng nhập, cho phép mọi role."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception:
            return error_response(
                error_code="UNAUTHORIZED",
                message="Bạn chưa đăng nhập hoặc phiên đăng nhập đã hết hạn.",
                status_code=401,
            )
        return fn(*args, **kwargs)
    return wrapper
