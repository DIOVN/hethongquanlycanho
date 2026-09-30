"""
SAMS Backend - Application Entry Point
Khởi chạy Flask development server hoặc được Gunicorn gọi trực tiếp.

Usage:
  Dev:  python run.py
  Prod: gunicorn -w 1 -b 0.0.0.0:5000 "run:app"
        (w=1 vì SQLite không hỗ trợ multi-process writer)
"""
import os
from app import create_app

# Tạo app instance - Gunicorn gọi module-level 'app'
app = create_app()

if __name__ == "__main__":
    # Chỉ chạy dev server khi gọi trực tiếp python run.py
    debug_mode = os.environ.get("ENVIRONMENT", "development") != "production"
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("BACKEND_PORT", 5000)),
        debug=debug_mode,
        use_reloader=True,
    )
