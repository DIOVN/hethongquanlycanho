---
name: sams-api-doc-generator
description: Tự động trích xuất và cập nhật tài liệu API.md từ mã nguồn Backend Flask sau khi code xong. Tự động phát hiện routes, decorators, schemas, parameters, mã lỗi và đồng bộ vào API contract của dự án.
---

# SAMS Automated API Documentation Generator Skill

Skill chuyên dụng cho phép hệ thống hoặc lập trình viên **tự động bổ sung, cập nhật và đồng bộ tài liệu `API.md`** ngay sau khi code xong Backend, giải phóng hoàn toàn công sức viết tài liệu thủ công và triệt tiêu nguy cơ sai lệch giữa Code và Hợp đồng API.

---

## 1. Mục Đích & Phạm Vi Kích Hoạt

### Khi nào kích hoạt skill này?
- **Ngay sau khi code xong một API mới:** Khi lập trình viên Backend hoặc AI Agent viết xong một hàm trong `backend/app/api/*.py`.
- **Khi cập nhật hoặc refactor route:** Khi thêm tham số mới, đổi phương thức (`GET` sang `POST`), thay đổi decorator phân quyền.
- **Trước khi chuyển giao sang Frontend:** Chạy kiểm tra để đảm bảo 100% endpoints trong Backend đã xuất hiện đầy đủ trong `API.md`.

---

## 2. Công Cụ Trích Xuất Tự Động (Automation Utility)

Skill cung cấp sẵn công cụ trích xuất tĩnh bằng Python AST tại:  
`scripts/extract_routes.py`

### Ưu điểm vượt trội:
1. **Hoàn toàn độc lập:** Chạy bằng Python Standard Library thuần (`ast`, `re`, `pathlib`), không yêu cầu cài đặt Flask hay chạy server.
2. **Không bỏ sót endpoint:** Quét qua toàn bộ các Blueprints trong `backend/app/api/`.
3. **Phân tích quyền hạn thông minh:** Tự nhận diện các decorators `@jwt_required`, `@admin_required`, `@landlord_required`, `@tenant_required` để ghi nhận mức độ bảo mật.
4. **Tự động hợp nhất (Smart Append):** Chỉ thêm các endpoint mới chưa có trong `API.md`, giữ nguyên các nội dung đã được trau chuốt trước đó.

---

## 3. Hướng Dẫn Thực Thi Lệnh (Command Guide)

Mở terminal tại thư mục gốc dự án (`hethongquanlycanho/`):

### 3.1. Tự động quét và cập nhật trực tiếp vào `API.md`:
```bash
python .agents/skills/sams-api-doc-generator/scripts/extract_routes.py
```
*Kết quả:* Script sẽ tìm kiếm các endpoint mới trong `backend/app/api/`, so khớp với `API.md` và tự động bổ sung khối đặc tả Markdown chuẩn mực vào cuối file.

### 3.2. Chỉ kiểm tra danh sách routes (Dry-run Check):
```bash
python .agents/skills/sams-api-doc-generator/scripts/extract_routes.py --check-only
```
*Kết quả mẫu:*
```text
🔍 Đang quét mã nguồn Backend tại: backend/app/api
✅ Đã trích xuất thành công 24 endpoint từ mã nguồn Backend!

📋 Danh sách Endpoints phát hiện được:
  [POST  ] /auth/register                     -> register() (Quyền: Public)
  [POST  ] /auth/login                        -> login() (Quyền: Public)
  [GET   ] /rooms/search                      -> search_rooms() (Quyền: Public)
  [POST  ] /rooms/<id>/roommates              -> add_roommate() (Quyền: Tenant)
  [POST  ] /quick-invoices                    -> create_quick_invoice() (Quyền: Landlord)
```

---

## 4. Chuẩn Viết Docstring Backend Để Xuất Tài Liệu Đẹp Nhất

Để tài liệu tự động sinh ra đạt chất lượng cao nhất cho đội ngũ Frontend, lập trình viên Backend cần viết docstring chuẩn Google / Sphinx format:

```python
# backend/app/api/roommates.py
from flask import Blueprint, request
from app.utils.decorators import tenant_required
from app.utils.response import success_response, error_response

roommates_bp = Blueprint("roommates", __name__)

@roommates_bp.route("/rooms/<int:room_id>/roommates", methods=["POST"])
@tenant_required
def add_roommate(room_id: int):
    """
    Khai báo thêm người ở cùng vào phòng căn hộ.
    
    Hàm tiếp nhận thông tin CCCD, họ tên, số điện thoại và biển số xe 
    để hỗ trợ chủ nhà làm thủ tục đăng ký tạm trú với Công an phường.

    Request JSON Body:
        full_name (str): Họ và tên đầy đủ của người ở cùng.
        cccd_number (str): Số Căn cước công dân (12 chữ số).
        phone (str): Số điện thoại liên hệ.
        vehicle_plate (str, optional): Biển số xe máy.

    Responses:
        201: Thêm thành viên thành công (trạng thái: pending).
        400: Số CCCD đã tồn tại trong hệ thống.
        403: Khách thuê không có quyền khai báo cho phòng khác.
    """
    # Logic xử lý tại đây...
    return success_response(data={"id": 1, "room_id": room_id}, status_code=201)
```

Khi có docstring trên, script `extract_routes.py` sẽ tự động phân tích:
- **Tóm tắt:** `Khai báo thêm người ở cùng vào phòng căn hộ.`
- **Mô tả chi tiết:** Toàn bộ đoạn văn bản nghiệp vụ.
- **Request Parameters & Mã lỗi:** Được định dạng đẹp mắt vào `API.md`.

---

## 5. Tích Hợp Vào Quy Trình Phát Triển (Workflow Integration)

Quy trình tuần tự của dự án giờ đây được nâng cấp thành:
1. **Bước 1 (Backend):** Lập trình viên Backend code xong các Models, Repositories, Services và Blueprints.
2. **Bước 2 (Auto API.md):** Chạy lệnh `python .agents/skills/sams-api-doc-generator/scripts/extract_routes.py`.
   $\rightarrow$ `API.md` tự động cập nhật ngay lập tức.
3. **Bước 3 (Frontend):** Lập trình viên Frontend mở `API.md` ra xem các endpoints mới nhất và tiến hành dựng giao diện.
