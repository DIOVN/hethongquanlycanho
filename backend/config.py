"""
SAMS Backend - Configuration Module
Tuân thủ 12-Factor App: Mọi cấu hình đến từ biến môi trường (.env)
"""
import os
from datetime import timedelta


class Config:
    """Base configuration class."""
    # --- Core ---
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "fallback-unsafe-key-change-me")
    ENVIRONMENT: str = os.environ.get("ENVIRONMENT", "development")

    # --- SQLAlchemy / SQLite ---
    _DEFAULT_BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    _raw_db_path = os.environ.get("SQLITE_DB_PATH", "/app/instance/apartment.db")
    if _raw_db_path.startswith("/app/") and not os.path.exists("/app"):
        SQLITE_DB_PATH: str = os.path.join(_DEFAULT_BASE_DIR, _raw_db_path.replace("/app/", "").replace("/", os.sep))
    else:
        SQLITE_DB_PATH: str = _raw_db_path
    SQLALCHEMY_DATABASE_URI: str = f"sqlite:///{SQLITE_DB_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ENGINE_OPTIONS: dict = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "connect_args": {
            "check_same_thread": False,
            "timeout": 30,
        },
    }

    # --- JWT ---
    JWT_SECRET_KEY: str = SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(
        minutes=int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", 1440))
    )
    JWT_REFRESH_TOKEN_EXPIRES: timedelta = timedelta(
        days=int(os.environ.get("JWT_REFRESH_TOKEN_EXPIRES_DAYS", 30))
    )
    JWT_ALGORITHM: str = "HS256"

    # --- CORS ---
    CORS_ORIGINS: list[str] = os.environ.get(
        "CORS_ORIGINS", "http://localhost:3000"
    ).split(",")

    # --- File Upload ---
    _raw_upload_folder: str = os.environ.get("UPLOAD_FOLDER", "/app/uploads")
    if _raw_upload_folder.startswith("/app/") and not os.path.exists("/app"):
        UPLOAD_FOLDER: str = os.path.join(_DEFAULT_BASE_DIR, _raw_upload_folder.replace("/app/", "").replace("/", os.sep))
    else:
        UPLOAD_FOLDER: str = _raw_upload_folder
    MAX_CONTENT_LENGTH: int = int(os.environ.get("MAX_CONTENT_LENGTH_MB", 10)) * 1024 * 1024
    ALLOWED_EXTENSIONS: set[str] = set(
        os.environ.get("ALLOWED_EXTENSIONS", "png,jpg,jpeg,webp").split(",")
    )

    # --- Gemini AI ---
    GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")
    GEMINI_TEXT_MODEL: str = os.environ.get("GEMINI_TEXT_MODEL", "gemini-1.5-flash")
    GEMINI_VISION_MODEL: str = os.environ.get("GEMINI_VISION_MODEL", "gemini-1.5-flash")
    GEMINI_TEMPERATURE: float = float(os.environ.get("GEMINI_TEMPERATURE", 0.2))

    # --- VietQR ---
    VIETQR_BANK_BIN: str = os.environ.get("VIETQR_BANK_BIN", "970422")
    VIETQR_BANK_NAME: str = os.environ.get("VIETQR_BANK_NAME", "MBBank")
    VIETQR_ACCOUNT_NUMBER: str = os.environ.get("VIETQR_ACCOUNT_NUMBER", "")
    VIETQR_ACCOUNT_NAME: str = os.environ.get("VIETQR_ACCOUNT_NAME", "")
    VIETQR_TEMPLATE: str = os.environ.get("VIETQR_TEMPLATE", "compact2")

    # --- Pricing Defaults ---
    DEFAULT_ELECTRICITY_PRICE_PER_KWH: float = float(
        os.environ.get("DEFAULT_ELECTRICITY_PRICE_PER_KWH", 3500)
    )
    DEFAULT_WATER_PRICE_PER_M3: float = float(
        os.environ.get("DEFAULT_WATER_PRICE_PER_M3", 25000)
    )
    DEFAULT_INTERNET_FEE_PER_ROOM: float = float(
        os.environ.get("DEFAULT_INTERNET_FEE_PER_ROOM", 100000)
    )
    DEFAULT_CLEANING_FEE_PER_ROOM: float = float(
        os.environ.get("DEFAULT_CLEANING_FEE_PER_ROOM", 50000)
    )

    # --- SMTP Email Configuration ---
    SMTP_HOST: str = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.environ.get("SMTP_PORT", 587))
    SMTP_USER: str = os.environ.get("SMTP_USER", "")
    SMTP_PASSWORD: str = os.environ.get("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL: str = os.environ.get("SMTP_FROM_EMAIL", os.environ.get("SMTP_USER", "no-reply@sams.local"))
    SMTP_FROM_NAME: str = os.environ.get("SMTP_FROM_NAME", "Hệ thống Quản lý Căn hộ SAMS")
    SMTP_USE_TLS: bool = os.environ.get("SMTP_USE_TLS", "true").lower() in ("true", "1", "yes")
    SMTP_USE_SSL: bool = os.environ.get("SMTP_USE_SSL", "false").lower() in ("true", "1", "yes")
    OTP_EXPIRY_MINUTES: int = int(os.environ.get("OTP_EXPIRY_MINUTES", 10))


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG: bool = True
    SQLALCHEMY_ECHO: bool = False  # Set True để log SQL queries khi debug


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG: bool = False
    SQLALCHEMY_ECHO: bool = False

    def __init__(self):
        # Kiểm tra bắt buộc các biến môi trường nhạy cảm trên Production
        required_vars = ["SECRET_KEY", "GEMINI_API_KEY", "VIETQR_ACCOUNT_NUMBER"]
        for var in required_vars:
            if not os.environ.get(var):
                raise EnvironmentError(f"[SAMS] Biến môi trường '{var}' bắt buộc trên Production!")


class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(minutes=5)
    WTF_CSRF_ENABLED: bool = False


# --- Config Registry ---
config_registry: dict[str, type] = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def get_config(environment: str | None = None) -> Config:
    """Trả về đối tượng cấu hình phù hợp với môi trường hiện tại."""
    env = environment or os.environ.get("ENVIRONMENT", "development")
    config_class = config_registry.get(env, DevelopmentConfig)
    return config_class()
