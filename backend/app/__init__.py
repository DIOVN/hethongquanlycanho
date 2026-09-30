"""
SAMS Backend - Application Factory
Tạo Flask app với Application Factory Pattern để dễ test và scale.
"""
import os
from flask import Flask
from dotenv import load_dotenv

# Load .env sớm nhất có thể trước khi import config
load_dotenv()

from config import get_config
from app.extensions import db, jwt, cors, migrate
from app.utils.db_sqlite import set_sqlite_pragma  # noqa: F401 - cần import để kích hoạt event listener


def create_app(config_name: str | None = None) -> Flask:
    """
    Flask Application Factory.

    Args:
        config_name: 'development' | 'production' | 'testing'.
                     Mặc định lấy từ biến môi trường ENVIRONMENT.

    Returns:
        Flask app instance đã được cấu hình hoàn chỉnh.
    """
    app = Flask(__name__, instance_relative_config=True)

    # --- Load Configuration ---
    cfg = get_config(config_name)
    app.config.from_object(cfg)

    # Đảm bảo thư mục instance và database tồn tại
    os.makedirs(app.instance_path, exist_ok=True)
    if "SQLITE_DB_PATH" in app.config and not app.config["SQLITE_DB_PATH"].startswith(":"):
        db_dir = os.path.dirname(app.config["SQLITE_DB_PATH"])
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

    # --- Initialize Extensions ---
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=True,
    )

    # --- Import Models để Flask-Migrate nhận biết schema ---
    with app.app_context():
        from app.models import (  # noqa: F401
            User, Building, Room, Contract, Roommate, RoomAsset,
            Invoice, InvoiceItem, UtilityReading, RoomViolation,
            Expense, BulletinAnnouncement, ServiceTicket, ChatSession,
        )

    # Đảm bảo thư mục upload tồn tại
    if "UPLOAD_FOLDER" in app.config:
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # --- Register Blueprints ---
    from app.api import (
        auth_bp, rooms_bp, roommates_bp, meters_bp,
        quick_invoices_bp, billing_bp, violations_bp,
        chat_bp, announcements_bp, tickets_bp,
        expenses_bp, contracts_bp,
    )
    app.register_blueprint(auth_bp)
    app.register_blueprint(rooms_bp)
    app.register_blueprint(roommates_bp)
    app.register_blueprint(meters_bp)
    app.register_blueprint(quick_invoices_bp)
    app.register_blueprint(billing_bp)
    app.register_blueprint(violations_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(announcements_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(contracts_bp)

    # --- Serve Uploaded Files ---
    from flask import send_from_directory

    @app.get("/uploads/<path:filename>")
    def serve_uploaded_file(filename: str):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    # --- Register Error Handlers ---
    _register_error_handlers(app)

    # --- Health Check Endpoint ---
    @app.get("/health")
    def health_check():
        from app.utils.response import success_response
        return success_response({"status": "healthy", "service": "SAMS Backend"})

    return app


def _register_error_handlers(app: Flask) -> None:
    """Đăng ký global error handlers cho các HTTP lỗi phổ biến."""
    from app.utils.response import error_response

    @app.errorhandler(400)
    def bad_request(e):
        return error_response("BAD_REQUEST", "Yêu cầu không hợp lệ.", 400)

    @app.errorhandler(404)
    def not_found(e):
        return error_response("NOT_FOUND", "Tài nguyên yêu cầu không tồn tại.", 404)

    @app.errorhandler(405)
    def method_not_allowed(e):
        return error_response("METHOD_NOT_ALLOWED", "Phương thức HTTP không được phép.", 405)

    @app.errorhandler(422)
    def unprocessable(e):
        return error_response("UNPROCESSABLE_ENTITY", "Dữ liệu không hợp lệ.", 422)

    @app.errorhandler(500)
    def internal_error(e):
        return error_response("INTERNAL_SERVER_ERROR", "Lỗi máy chủ nội bộ.", 500)

    # JWT error handlers
    from flask_jwt_extended import JWTManager
    from app.extensions import jwt as jwt_manager

    @jwt_manager.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return error_response("TOKEN_EXPIRED", "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.", 401)

    @jwt_manager.invalid_token_loader
    def invalid_token_callback(error_string):
        return error_response("INVALID_TOKEN", "Token không hợp lệ hoặc đã bị sửa đổi.", 401)

    @jwt_manager.unauthorized_loader
    def missing_token_callback(error_string):
        return error_response("MISSING_TOKEN", "Bạn cần đăng nhập để thực hiện thao tác này.", 401)
