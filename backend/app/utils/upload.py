"""
SAMS - File Upload Helper
Lưu trữ an toàn các file ảnh công tơ, biên lai thanh toán và bằng chứng vi phạm.
"""
import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app


def save_uploaded_file(file_storage, subfolder: str = "general") -> str:
    """
    Lưu file upload vào thư mục chỉ định và trả về relative URL.

    Args:
        file_storage: Werkzeug FileStorage object từ request.files.
        subfolder: Thư mục con (meters, slips, violations, tickets).

    Returns:
        Đường dẫn relative URL để lưu vào DB (ví dụ: '/uploads/meters/xyz.jpg').
    """
    if not file_storage or not file_storage.filename:
        raise ValueError("Không có file tải lên hoặc tên file rỗng.")

    filename = secure_filename(file_storage.filename)
    ext = filename.rsplit(".", 1)[1].lower() if "." in filename else "jpg"
    allowed = current_app.config.get("ALLOWED_EXTENSIONS", {"png", "jpg", "jpeg", "webp"})
    if ext not in allowed:
        raise ValueError(f"Định dạng file '.{ext}' không được hỗ trợ. Hợp lệ: {allowed}")

    # Tạo tên file duy nhất chống ghi đè
    unique_name = f"{uuid.uuid4().hex[:12]}_{filename}"

    upload_root = current_app.config.get("UPLOAD_FOLDER")
    target_dir = os.path.join(upload_root, subfolder)
    os.makedirs(target_dir, exist_ok=True)

    file_path = os.path.join(target_dir, unique_name)
    file_storage.save(file_path)

    # Trả về relative URL
    return f"/uploads/{subfolder}/{unique_name}"
