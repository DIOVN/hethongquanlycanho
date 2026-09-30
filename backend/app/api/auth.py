"""
SAMS - Auth API Controller
Endpoints: /api/v1/auth/register, /api/v1/auth/login, /api/v1/auth/me
Tuân thủ API.md §3.1
"""
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, get_jwt

from app.services.auth_service import AuthService
from app.utils.response import success_response, error_response
from app.utils.decorators import authenticated_required

auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@auth_bp.post("/register/send-otp")
def send_register_otp():
    """
    POST /api/v1/auth/register/send-otp
    Gửi mã OTP 6 số qua email để xác thực đăng ký tài khoản.
    Public endpoint.
    """
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip()

    if not email:
        return error_response("MISSING_EMAIL", "Địa chỉ email là bắt buộc.", 422)

    res, error_code = AuthService.request_registration_otp(email)
    if error_code:
        messages = {
            "INVALID_EMAIL": "Địa chỉ email không đúng định dạng.",
            "EMAIL_EXISTS": "Địa chỉ email này đã được sử dụng bởi một tài khoản khác.",
        }
        return error_response(
            error_code,
            messages.get(error_code, "Không thể gửi mã xác thực OTP."),
            400,
        )

    return success_response(res, message="Mã xác thực OTP đã được gửi đến email của bạn.")


@auth_bp.post("/register")
def register():
    """
    POST /api/v1/auth/register
    Đăng ký tài khoản mới kèm mã xác thực OTP (role mặc định: tenant).
    Public endpoint - không cần JWT.
    """
    data = request.get_json(silent=True)
    if not data:
        return error_response("INVALID_JSON", "Request body phải là JSON hợp lệ.", 400)

    # Kiểm tra các trường bắt buộc
    required_fields = ["username", "email", "password", "full_name"]
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        return error_response(
            "MISSING_REQUIRED_FIELDS",
            f"Thiếu các trường bắt buộc: {', '.join(missing)}.",
            422,
            {"missing_fields": missing},
        )

    # Kiểm tra độ dài mật khẩu tối thiểu
    if len(data["password"]) < 8:
        return error_response(
            "WEAK_PASSWORD",
            "Mật khẩu phải có ít nhất 8 ký tự.",
            422,
        )

    user, error_code = AuthService.register(
        username=data["username"],
        email=data["email"],
        password=data["password"],
        full_name=data["full_name"],
        phone=data.get("phone"),
        cccd_number=data.get("cccd_number"),
        otp_code=data.get("otp_code"),
    )

    if error_code:
        messages = {
            "USERNAME_EXISTS": "Tên đăng nhập đã tồn tại trong hệ thống.",
            "EMAIL_EXISTS": "Địa chỉ email đã được sử dụng.",
            "INVALID_PHONE": "Số điện thoại không hợp lệ (định dạng Việt Nam: 0xxx hoặc +84xxx).",
            "DATABASE_ERROR": "Có lỗi khi lưu dữ liệu, vui lòng thử lại.",
            "INVALID_OTP": "Mã xác thực OTP không chính xác. Vui lòng kiểm tra lại.",
            "OTP_EXPIRED": "Mã OTP đã hết hiệu lực hoặc chưa được khởi tạo. Vui lòng lấy mã mới.",
        }
        return error_response(
            error_code,
            messages.get(error_code, "Đăng ký thất bại."),
            400 if error_code not in ("INVALID_PHONE", "INVALID_OTP") else 422,
        )

    return success_response(user.to_dict(), status_code=201)


@auth_bp.post("/forgot-password")
def forgot_password():
    """
    POST /api/v1/auth/forgot-password
    Gửi mã OTP đặt lại mật khẩu qua email.
    Public endpoint.
    """
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip()

    if not email:
        return error_response("MISSING_EMAIL", "Địa chỉ email là bắt buộc.", 422)

    res, error_code = AuthService.request_password_reset_otp(email)
    if error_code:
        messages = {
            "INVALID_EMAIL": "Địa chỉ email không đúng định dạng.",
            "USER_NOT_FOUND": "Không tìm thấy tài khoản liên kết với địa chỉ email này.",
        }
        return error_response(
            error_code,
            messages.get(error_code, "Không thể gửi mã xác thực đặt lại mật khẩu."),
            400 if error_code != "USER_NOT_FOUND" else 404,
        )

    return success_response(res, message="Mã xác thực OTP đặt lại mật khẩu đã được gửi đến email.")


@auth_bp.post("/reset-password")
def reset_password():
    """
    POST /api/v1/auth/reset-password
    Xác minh mã OTP và cập nhật mật khẩu mới.
    Public endpoint.
    """
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip()
    otp_code = data.get("otp_code", "").strip()
    new_password = data.get("new_password", "")

    if not email or not otp_code or not new_password:
        return error_response(
            "MISSING_FIELDS",
            "Email, mã OTP và mật khẩu mới là bắt buộc.",
            422,
        )

    if len(new_password) < 8:
        return error_response("WEAK_PASSWORD", "Mật khẩu mới phải có ít nhất 8 ký tự.", 422)

    success, error_code = AuthService.reset_password(email, otp_code, new_password)
    if error_code:
        messages = {
            "OTP_EXPIRED": "Mã xác thực OTP đã hết hạn hoặc không tồn tại. Vui lòng yêu cầu mã mới.",
            "INVALID_OTP": "Mã OTP không chính xác. Vui lòng kiểm tra lại.",
            "USER_NOT_FOUND": "Không tìm thấy tài khoản người dùng.",
            "WEAK_PASSWORD": "Mật khẩu mới phải có ít nhất 8 ký tự.",
        }
        return error_response(
            error_code,
            messages.get(error_code, "Đặt lại mật khẩu thất bại."),
            400 if error_code != "USER_NOT_FOUND" else 404,
        )

    return success_response(
        data={"email": email},
        message="Đặt lại mật khẩu thành công! Bạn có thể đăng nhập ngay với mật khẩu mới."
    )


@auth_bp.post("/login")
def login():
    """
    POST /api/v1/auth/login
    Đăng nhập và nhận JWT Access + Refresh tokens.
    Public endpoint - không cần JWT.
    """
    data = request.get_json(silent=True)
    if not data:
        return error_response("INVALID_JSON", "Request body phải là JSON hợp lệ.", 400)

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return error_response(
            "MISSING_CREDENTIALS",
            "Tên đăng nhập và mật khẩu là bắt buộc.",
            422,
        )

    token_data, error_code = AuthService.login(username, password)

    if error_code:
        return error_response(
            "INVALID_CREDENTIALS",
            "Tên đăng nhập hoặc mật khẩu không chính xác.",
            401,
        )

    return success_response(token_data, status_code=200)


@auth_bp.get("/me")
@authenticated_required
def get_profile():
    """
    GET /api/v1/auth/me
    Lấy thông tin hồ sơ tài khoản đang đăng nhập.
    Yêu cầu JWT token hợp lệ.
    """
    user_id = int(get_jwt_identity())
    user = AuthService.get_user_by_id(user_id)

    if not user:
        return error_response("USER_NOT_FOUND", "Tài khoản không tồn tại.", 404)

    return success_response(user.to_dict())
