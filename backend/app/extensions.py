"""
SAMS Backend - Flask Extensions Module
Khởi tạo tất cả các extension một lần, tránh circular imports.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate

# --- Khởi tạo extension instances (chưa bind với app) ---
db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()
migrate = Migrate()
