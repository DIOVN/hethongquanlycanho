"""
SAMS - SQLite WAL Mode & Performance PRAGMA Configuration
Cấu hình SQLite tối ưu cho concurrency cao, đặc biệt khi MCP Server đọc
đồng thời với Flask Backend ghi dữ liệu.
"""
import sqlite3
from sqlalchemy import event
from sqlalchemy.engine import Engine


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Lắng nghe sự kiện kết nối SQLAlchemy và thiết lập PRAGMA ngay lập tức.
    Đây là điểm duy nhất cần cấu hình - áp dụng cho mọi connection trong pool.
    """
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()

        # Write-Ahead Logging: Cho phép nhiều readers đọc song song khi có 1 writer
        cursor.execute("PRAGMA journal_mode = WAL;")

        # Tối ưu I/O commit: Giảm thời gian chờ fsync mà vẫn đảm bảo an toàn ACID
        cursor.execute("PRAGMA synchronous = NORMAL;")

        # Thời gian xếp hàng chờ khi có ghi: 30 giây (triệt tiêu lỗi "database is locked")
        cursor.execute("PRAGMA busy_timeout = 30000;")

        # Bật toàn vẹn khóa ngoại - QUAN TRỌNG cho data integrity
        cursor.execute("PRAGMA foreign_keys = ON;")

        # Cấp phát 64MB In-memory Cache cho kết nối
        cursor.execute("PRAGMA cache_size = -64000;")

        # Sử dụng RAM thay vì đĩa cho bảng tạm (tăng tốc JOIN & ORDER BY phức tạp)
        cursor.execute("PRAGMA temp_store = MEMORY;")

        # Tối ưu mmap I/O - đọc 128MB qua memory-mapped I/O
        cursor.execute("PRAGMA mmap_size = 134217728;")

        cursor.close()
