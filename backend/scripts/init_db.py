"""
SAMS - Database Initialization Script
Tạo tất cả bảng và seed dữ liệu admin ban đầu.
Chạy một lần duy nhất khi khởi tạo hệ thống.

Usage: python scripts/init_db.py
"""
import sys
import os

# Thêm thư mục backend vào PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.extensions import db
from app.services.auth_service import AuthService


def init_database():
    """Khởi tạo database và seed admin account mặc định."""
    app = create_app()

    with app.app_context():
        print("🔧 Đang tạo các bảng database...")
        db.create_all()
        print("✅ Tạo bảng thành công!")

        # Seed admin account nếu chưa tồn tại
        from app.models.user import User
        admin_username = os.environ.get("ADMIN_USERNAME", "admin")
        existing_admin = User.query.filter_by(username=admin_username).first()

        if not existing_admin:
            print(f"🌱 Đang tạo tài khoản admin: {admin_username}...")
            admin = User(
                username=admin_username,
                email=os.environ.get("ADMIN_EMAIL", "admin@sams.local"),
                password_hash=AuthService.hash_password(
                    os.environ.get("ADMIN_PASSWORD", "Admin@SAMS2024!")
                ),
                full_name="Quản trị viên Hệ thống",
                role="admin",
                phone=None,
            )
            db.session.add(admin)
            db.session.commit()
            print(f"✅ Tài khoản admin đã được tạo!")
            print(f"   Username: {admin_username}")
            print(f"   Mật khẩu: {os.environ.get('ADMIN_PASSWORD', 'Admin@SAMS2024!')}")
            print(f"   ⚠️  Hãy đổi mật khẩu ngay sau khi đăng nhập lần đầu!")
        else:
            print(f"ℹ️  Tài khoản admin '{admin_username}' đã tồn tại, bỏ qua seed.")

        # In thống kê bảng
        from sqlalchemy import inspect, text
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"\n📊 Database đã tạo {len(tables)} bảng:")
        for table in sorted(tables):
            count = db.session.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"   ✓ {table} ({count} bản ghi)")

    print("\n🚀 Khởi tạo database SAMS hoàn tất!")


if __name__ == "__main__":
    init_database()
