# SAMS RESTful API Specification (API.md)
**Hệ thống Quản lý Căn hộ Cho thuê Tích hợp Trí tuệ Nhân tạo (SAMS)**  
**Tài liệu Hợp đồng Kỹ thuật (API Contract - Single Source of Truth)**  
**Phiên bản:** 1.0.0  
**Ngày cập nhật:** 01/10/2026  
**Quy chuẩn áp dụng:** RESTful JSON:API Envelope, JWT Bearer Authentication, RFC 7807 Error Model  

> [!IMPORTANT]
> **Quy tắc Kỷ luật Kỹ thuật (Sequential Engineering Rule):**  
> 1. Toàn bộ mã nguồn Frontend (React SPA) **BẮT BUỘC** phải tuân theo 100% tài liệu này làm căn cứ xác thực kiểu dữ liệu, endpoint URL, method và cấu trúc payload.  
> 2. Lập trình viên Frontend tuyệt đối không tự ý đổi tên trường (`field_name`), không tự bịa endpoint hay giả định cấu trúc trả về khác với tài liệu này.  
> 3. Khi Backend có thay đổi, lập trình viên Backend phải cập nhật `API.md` trước và thông báo cho Frontend.

---

## 1. Cấu Trúc Tổng Quan (Global Architecture)

### 1.1. Base URL
- Local Development: `http://localhost:5000/api/v1`
- Nginx Reverse Proxy / Docker Compose: `http://localhost/api/v1`

### 1.2. Headers Chuẩn
| Header | Giá trị bắt buộc | Áp dụng cho |
| :--- | :--- | :--- |
| `Content-Type` | `application/json` (hoặc `multipart/form-data` khi tải ảnh) | Mọi request gửi body |
| `Authorization` | `Bearer <jwt_access_token>` | Các endpoint yêu cầu đăng nhập |
| `Accept` | `application/json` | Mọi request |

### 1.3. Cấu Trúc Envelope Phản Hồi Chuẩn (Standard Response Envelope)

Tất cả các phản hồi từ Backend **BẮT BUỘC** được bọc trong cấu trúc JSON Envelope đồng nhất:

#### Phản hồi Thành công (`success: true`):
```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "timestamp": "2026-10-01T12:00:00Z",
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total_items": 45,
      "total_pages": 3
    }
  },
  "error": null
}
```

#### Phản hồi Thất bại (`success: false`):
```json
{
  "success": false,
  "data": null,
  "meta": {
    "timestamp": "2026-10-01T12:00:00Z"
  },
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Tên đăng nhập hoặc mật khẩu không chính xác.",
    "details": {}
  }
}
```

---

## 2. Bảng Tổng Hợp Endpoints Hệ Thống

| Phân hệ (Module) | Method | Endpoint | Quyền hạn | Chức năng nghiệp vụ |
| :--- | :--- | :--- | :--- | :--- |
| **Auth** | `POST` | `/auth/register` | Public | Đăng ký tài khoản khách thuê mới |
| **Auth** | `POST` | `/auth/login` | Public | Đăng nhập nhận JWT Access & Refresh Token |
| **Auth** | `GET` | `/auth/me` | Authenticated | Lấy hồ sơ tài khoản đang đăng nhập |
| **Rooms** | `GET` | `/rooms` | Landlord/Admin | Danh sách tất cả các phòng trong tòa nhà |
| **Rooms** | `GET` | `/rooms/search` | Public/Tenant | Tìm kiếm phòng trống theo bộ lọc giá, diện tích |
| **Rooms** | `GET` | `/rooms/my-room` | Tenant | Lấy thông tin phòng và hợp đồng của khách thuê |
| **Roommates** | `GET` | `/rooms/{id}/roommates` | Landlord/Tenant | Xem danh sách thành viên đang ở trong phòng |
| **Roommates** | `POST` | `/rooms/{id}/roommates` | Landlord/Tenant | Khai báo thêm thành viên ở cùng (CCCD, SĐT, xe) |
| **Roommates** | `PUT` | `/rooms/{id}/roommates/{rid}/status`| Landlord | Cập nhật duyệt trạng thái tạm trú Công an |
| **Meters** | `POST` | `/meters/scan-reading` | Tenant | Tải ảnh công tơ điện nước lên để Gemini Vision OCR |
| **Meters** | `POST` | `/meters/confirm-reading`| Tenant | Khách xác nhận ghi nhận số đo vào database |
| **Invoices** | `POST` | `/quick-invoices` | Landlord/Admin | Tạo hóa đơn nhanh tại chỗ từ ảnh chụp công tơ |
| **Billing** | `GET` | `/billing/my-invoices` | Tenant | Lấy danh sách hóa đơn của khách (kèm VietQR) |
| **Billing** | `POST` | `/billing/{id}/payment-slip` | Tenant | Tải ảnh chụp biên lai giao dịch chuyển khoản |
| **Billing** | `POST` | `/billing/generate` | Landlord/Admin | Tự động tính tiền và phát hành hóa đơn hàng loạt |
| **Violations** | `GET` | `/violations` | Landlord/Admin | Danh sách biên bản vi phạm nội quy tòa nhà |
| **Violations** | `POST` | `/violations` | Landlord/Admin | Lập biên bản cảnh cáo / phạt vi phạm phòng |
| **Violations** | `PUT` | `/violations/{id}/acknowledge` | Tenant | Khách xác nhận đã đọc và cam kết không tái phạm |
| **Assets** | `POST` | `/assets/verify` | Tenant | Khách xác nhận checklist đồ đạc lúc nhận phòng |
| **Expenses** | `POST` | `/expenses` | Landlord/Admin | Ghi nhận chi phí vận hành OpEx mới |
| **Expenses** | `GET` | `/expenses/net-profit` | Landlord/Admin | Báo cáo Lợi nhuận Ròng (Doanh thu - OpEx) |
| **Contracts** | `POST` | `/contracts/refund` | Landlord/Admin | Quyết toán hoàn tiền cọc khi khách trả phòng |
| **Chatbot** | `POST` | `/chat/message` | Tenant | Đàm thoại tự nhiên với Trợ lý ảo Gemini |
| **Bulletin** | `GET` | `/announcements` | Tenant/Landlord | Xem danh sách thông báo bảng tin |

---

## 3. Đặc Tả Chi Tiết Từng Endpoint

### 3.1. Phân hệ Xác thực (Authentication Module)

#### `POST /auth/register`
- **Mô tả:** Đăng ký tài khoản người dùng mới. Mặc định gán `role = 'tenant'`.
- **Quyền truy cập:** `Public`
- **Request Body:**
```json
{
  "username": "nguyenvana",
  "email": "nguyenvana@gmail.com",
  "password": "Password123@",
  "full_name": "Nguyễn Văn A",
  "phone": "0987654321",
  "cccd_number": "079198000123"
}
```
- **Response Thành công (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": 12,
    "username": "nguyenvana",
    "email": "nguyenvana@gmail.com",
    "full_name": "Nguyễn Văn A",
    "role": "tenant",
    "created_at": "2026-10-01T08:00:00Z"
  },
  "meta": { "timestamp": "2026-10-01T08:00:00Z" },
  "error": null
}
```
- **Mã lỗi:** `400 USERNAME_EXISTS`, `400 EMAIL_EXISTS`, `422 INVALID_PHONE`.

---

#### `POST /auth/login`
- **Mô tả:** Đăng nhập hệ thống, trả về JWT Access Token (24h) và Refresh Token (30 ngày).
- **Quyền truy cập:** `Public`
- **Request Body:**
```json
{
  "username": "nguyenvana",
  "password": "Password123@"
}
```
- **Response Thành công (200 OK):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 86400,
    "user": {
      "id": 12,
      "username": "nguyenvana",
      "full_name": "Nguyễn Văn A",
      "role": "tenant"
    }
  },
  "meta": { "timestamp": "2026-10-01T08:05:00Z" },
  "error": null
}
```
- **Mã lỗi:** `401 INVALID_CREDENTIALS`.

---

### 3.2. Phân hệ Phòng & Tìm kiếm (Rooms & Search Module)

#### `GET /rooms/search`
- **Mô tả:** Tìm kiếm danh mục phòng trống cho khách thuê vãng lai hoặc nội bộ.
- **Quyền truy cập:** `Public`
- **Query Parameters:**
  - `min_price` (number, optional): Giá tối thiểu (VNĐ).
  - `max_price` (number, optional): Giá tối đa (VNĐ).
  - `min_area` (number, optional): Diện tích tối thiểu ($m^2$).
  - `floor` (integer, optional): Tầng cụ thể.
- **Response Thành công (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 5,
      "building_name": "SAMS Building 1",
      "address": "123 Đường Điện Biên Phủ, Q. Bình Thạnh, TP.HCM",
      "room_number": "302",
      "floor": 3,
      "base_price": 4500000.0,
      "area_sqm": 28.5,
      "status": "vacant",
      "has_balcony": true
    }
  ],
  "meta": {
    "timestamp": "2026-10-01T08:10:00Z",
    "total": 1
  },
  "error": null
}
```

---

#### `GET /rooms/my-room`
- **Mô tả:** Lấy thông tin chi tiết phòng và hợp đồng của khách thuê hiện tại dựa trên JWT Token.
- **Quyền truy cập:** `Tenant` (Bắt buộc Header `Authorization: Bearer <token>`).
- **Response Thành công (200 OK):**
```json
{
  "success": true,
  "data": {
    "room_id": 5,
    "room_number": "302",
    "building_name": "SAMS Building 1",
    "building_address": "123 Điện Biên Phủ, Q. Bình Thạnh",
    "area_sqm": 28.5,
    "monthly_rent": 4500000.0,
    "deposit_amount": 4500000.0,
    "contract_id": 2,
    "start_date": "2026-06-01",
    "end_date": "2027-06-01",
    "contract_status": "active",
    "total_roommates": 2
  },
  "meta": { "timestamp": "2026-10-01T08:15:00Z" },
  "error": null
}
```
- **Mã lỗi:** `404 ACTIVE_CONTRACT_NOT_FOUND` (nếu tài khoản chưa được gán vào hợp đồng nào).

---

### 3.3. Phân hệ Quản lý Nhân khẩu & Ở cùng (Roommates Module)

#### `GET /rooms/{id}/roommates`
- **Mô tả:** Lấy danh sách tất cả các thành viên đang cư trú trong phòng.
- **Quyền truy cập:** `Tenant` (chính phòng đó) hoặc `Landlord/Admin`.
- **Response Thành công (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "full_name": "Nguyễn Văn A",
      "phone": "0987654321",
      "cccd_number": "079198000123",
      "date_of_birth": "1998-05-12",
      "gender": "male",
      "hometown": "Long An",
      "vehicle_plate": "62-B1 123.45",
      "is_primary_tenant": true,
      "temporary_residence_status": "registered",
      "created_at": "2026-06-01T10:00:00Z"
    },
    {
      "id": 2,
      "full_name": "Trần Thị B",
      "phone": "0912345678",
      "cccd_number": "079200000456",
      "date_of_birth": "2000-11-20",
      "gender": "female",
      "hometown": "Bến Tre",
      "vehicle_plate": "71-C2 678.90",
      "is_primary_tenant": false,
      "temporary_residence_status": "pending",
      "created_at": "2026-08-15T14:20:00Z"
    }
  ],
  "meta": { "timestamp": "2026-10-01T08:20:00Z" },
  "error": null
}
```

---

#### `POST /rooms/{id}/roommates`
- **Mô tả:** Đăng ký thêm thành viên vào ở cùng trong phòng.
- **Quyền truy cập:** `Tenant` (đại diện phòng) hoặc `Landlord`.
- **Request Body:**
```json
{
  "full_name": "Lê Văn C",
  "phone": "0933333333",
  "cccd_number": "079199000789",
  "date_of_birth": "1999-09-09",
  "gender": "male",
  "hometown": "Đồng Nai",
  "vehicle_plate": "60-F2 888.88"
}
```
- **Response Thành công (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": 3,
    "room_id": 5,
    "full_name": "Lê Văn C",
    "temporary_residence_status": "pending",
    "created_at": "2026-10-01T08:25:00Z"
  },
  "meta": { "timestamp": "2026-10-01T08:25:00Z" },
  "error": null
}
```
- **Mã lỗi:** `400 CCCD_ALREADY_REGISTERED`, `422 INVALID_CCCD_FORMAT` (phải đúng 12 chữ số).

---

### 3.4. Phân hệ Đo số Điện Nước & Gemini Vision OCR

#### `POST /meters/scan-reading`
- **Mô tả:** Gửi ảnh công tơ điện hoặc nước để Gemini 1.5 Flash Vision OCR trích xuất chỉ số.
- **Quyền truy cập:** `Tenant` hoặc `Landlord`
- **Headers:** `Content-Type: multipart/form-data`
- **Form Data:**
  - `image`: File ảnh chụp công tơ (png, jpg, jpeg, webp $\le 10MB$).
  - `meter_type`: `electricity` hoặc `water`.
  - `room_id`: integer (ID phòng).
- **Response Thành công (200 OK):**
```json
{
  "success": true,
  "data": {
    "detected_reading": 1428.0,
    "confidence": 0.96,
    "meter_type": "electricity",
    "previous_reading": 1343.0,
    "consumption": 85.0,
    "temporary_image_url": "/uploads/meters/temp_meter_302_elec_20261001.jpg",
    "warning_flag": null
  },
  "meta": { "timestamp": "2026-10-01T08:30:00Z" },
  "error": null
}
```
- **Lưu ý kiểm tra:** Nếu `detected_reading < previous_reading`, trường `warning_flag` sẽ có giá trị `"READING_LOWER_THAN_PREVIOUS"`.

---

#### `POST /meters/confirm-reading`
- **Mô tả:** Khách hoặc chủ nhà xác nhận lưu chỉ số công tơ chính thức vào CSDL.
- **Request Body:**
```json
{
  "room_id": 5,
  "meter_type": "electricity",
  "confirmed_reading": 1428.0,
  "image_url": "/uploads/meters/temp_meter_302_elec_20261001.jpg",
  "ai_confidence": 0.96
}
```
- **Response Thành công (201 Created):**
```json
{
  "success": true,
  "data": {
    "reading_id": 42,
    "room_id": 5,
    "meter_type": "electricity",
    "reading_value": 1428.0,
    "consumption": 85.0,
    "month": 10,
    "year": 2026,
    "recorded_at": "2026-10-01T08:32:00Z"
  },
  "meta": { "timestamp": "2026-10-01T08:32:00Z" },
  "error": null
}
```

---

### 3.5. Phân hệ Tạo Hóa Đơn Nhanh & Thanh Toán VietQR

#### `POST /quick-invoices`
- **Mô tả:** Chủ nhà chụp ảnh công tơ tại chỗ, AI nhận diện và xuất bản hóa đơn kèm ảnh bằng chứng ngay lập tức.
- **Quyền truy cập:** `Landlord` hoặc `Admin`
- **Headers:** `Content-Type: multipart/form-data`
- **Form Data:**
  - `room_id`: integer
  - `month`: integer (1-12)
  - `year`: integer (2026)
  - `electricity_image`: File ảnh công tơ điện
  - `electricity_reading`: float (tùy chọn, ghi đè nếu chỉnh tay)
  - `water_image`: File ảnh công tơ nước
  - `water_reading`: float (tùy chọn, ghi đè nếu chỉnh tay)
- **Response Thành công (201 Created):**
```json
{
  "success": true,
  "data": {
    "invoice_id": 108,
    "room_number": "302",
    "month": 10,
    "year": 2026,
    "total_amount": 5147500.0,
    "status": "unpaid",
    "vietqr_url": "https://img.vietqr.io/image/970422-0987654321-compact2.png?amount=5147500&addInfo=SAMS%20P302%20T10",
    "items": [
      { "item_type": "rent", "description": "Tiền phòng T10/2026", "subtotal": 4500000.0 },
      { "item_type": "electricity", "description": "Điện: 85 kWh x 3.500đ", "subtotal": 297500.0 },
      { "item_type": "water", "description": "Nước: 6 m3 x 25.000đ", "subtotal": 150000.0 },
      { "item_type": "service", "description": "Internet & Dịch vụ rác", "subtotal": 150000.0 },
      { "item_type": "penalty", "description": "Phạt tiếng ồn sau 22h (Biên bản #14)", "subtotal": 50000.0 }
    ],
    "evidence_images": {
      "electricity_meter": "/uploads/meters/p302_elec_t10.jpg",
      "water_meter": "/uploads/meters/p302_water_t10.jpg"
    }
  },
  "meta": { "timestamp": "2026-10-01T08:40:00Z" },
  "error": null
}
```

---

#### `GET /billing/my-invoices`
- **Mô tả:** Khách thuê xem danh sách các hóa đơn của phòng mình.
- **Quyền truy cập:** `Tenant`
- **Response Thành công (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 108,
      "month": 10,
      "year": 2026,
      "total_amount": 5147500.0,
      "status": "unpaid",
      "due_date": "2026-10-05",
      "vietqr_payload": "00020101021238540010A00000072701240006970422011009876543210208QRIBFTTA5303704540751475005802VN62170813SAMS P302 T10630465E2",
      "vietqr_image_url": "https://img.vietqr.io/image/970422-0987654321-compact2.png?amount=5147500&addInfo=SAMS%20P302%20T10",
      "payment_ref": "SAMS P302 T10"
    }
  ],
  "meta": { "timestamp": "2026-10-01T08:45:00Z" },
  "error": null
}
```

---

#### `POST /billing/{id}/payment-slip`
- **Mô tả:** Khách thuê tải ảnh chụp màn hình biên lai chuyển khoản ngân hàng.
- **Quyền truy cập:** `Tenant`
- **Headers:** `Content-Type: multipart/form-data`
- **Form Data:**
  - `slip_image`: File ảnh biên lai giao dịch ngân hàng
- **Response Thành công (200 OK):**
```json
{
  "success": true,
  "data": {
    "invoice_id": 108,
    "status": "pending_verification",
    "slip_image_url": "/uploads/slips/slip_invoice_108_20261001.jpg",
    "submitted_at": "2026-10-01T08:50:00Z"
  },
  "meta": { "timestamp": "2026-10-01T08:50:00Z" },
  "error": null
}
```

---

### 3.6. Phân hệ Cảnh Báo Vi Phạm & Kỷ Luật (Violations Module)

#### `GET /violations`
- **Mô tả:** Danh sách các biên bản vi phạm nội quy toàn tòa nhà (hoặc lọc theo `room_id`).
- **Quyền truy cập:** `Landlord/Admin` hoặc `Tenant` (chỉ xem phòng mình).
- **Query Parameters:** `room_id` (optional), `status` (optional: `pending`, `acknowledged`, `penalized`, `resolved`).
- **Response Thành công (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 14,
      "room_id": 5,
      "room_number": "302",
      "violation_type": "noise",
      "severity": "penalty",
      "title": "Gây tiếng ồn lớn sau 23h đêm",
      "description": "Phòng 302 tụ tập hát karaoke mở loa kéo âm lượng lớn gây ảnh hưởng phòng 301 và 303.",
      "evidence_image_url": "/uploads/violations/evidence_noise_302.jpg",
      "penalty_amount": 200000.0,
      "status": "penalized",
      "created_at": "2026-09-28T23:45:00Z"
    }
  ],
  "meta": { "timestamp": "2026-10-01T08:55:00Z" },
  "error": null
}
```

---

#### `POST /violations`
- **Mô tả:** Chủ nhà lập biên bản cảnh cáo hoặc phạt tiền phòng vi phạm nội quy.
- **Quyền truy cập:** `Landlord` hoặc `Admin`
- **Request Body:**
```json
{
  "room_id": 5,
  "violation_type": "noise",
  "severity": "penalty",
  "title": "Hát karaoke sau 23h đêm",
  "description": "Bị phản ánh bởi phòng 301 và 303, bảo vệ đã nhắc nhở 2 lần nhưng vẫn tiếp diễn.",
  "evidence_image_url": "/uploads/violations/evidence_noise_302.jpg",
  "penalty_amount": 200000.0
}
```
- **Response Thành công (201 Created):**
```json
{
  "success": true,
  "data": {
    "violation_id": 15,
    "room_id": 5,
    "severity": "penalty",
    "penalty_amount": 200000.0,
    "status": "pending",
    "created_at": "2026-10-01T09:00:00Z"
  },
  "meta": { "timestamp": "2026-10-01T09:00:00Z" },
  "error": null
}
```

---

#### `PUT /violations/{id}/acknowledge`
- **Mô tả:** Khách thuê xác nhận đã nhận thông báo nhắc nhở / cảnh cáo và ký cam kết điện tử.
- **Quyền truy cập:** `Tenant` (thuộc phòng vi phạm)
- **Response Thành công (200 OK):**
```json
{
  "success": true,
  "data": {
    "violation_id": 15,
    "status": "acknowledged",
    "acknowledged_at": "2026-10-01T09:05:00Z"
  },
  "meta": { "timestamp": "2026-10-01T09:05:00Z" },
  "error": null
}
```

---

### 3.7. Phân hệ Trợ Lý Ảo Gemini Đàm Thoại (AI Chat Assistant)

#### `POST /chat/message`
- **Mô tả:** Gửi tin nhắn đàm thoại tự nhiên với Trợ lý ảo AI tòa nhà. AI tự động gọi Function Calling khi hỏi tiền phòng hoặc báo hỏng.
- **Quyền truy cập:** `Tenant`
- **Request Body:**
```json
{
  "message": "Tháng này phòng tôi hết bao nhiêu tiền điện?"
}
```
- **Response Thành công (200 OK):**
```json
{
  "success": true,
  "data": {
    "reply": "Chào bạn! Trong tháng 10/2026, phòng 302 của bạn tiêu thụ 85 kWh điện (chỉ số mới: 1428, chỉ số cũ: 1343). Thành tiền điện là 297.500đ. Tổng hóa đơn tháng này của phòng là 5.147.500đ. Bạn có muốn quét mã VietQR để thanh toán ngay không?",
    "function_called": "get_unpaid_invoices",
    "attached_action": {
      "type": "VIETQR_PAYMENT_CARD",
      "invoice_id": 108,
      "amount": 5147500.0,
      "vietqr_url": "https://img.vietqr.io/image/970422-0987654321-compact2.png?amount=5147500&addInfo=SAMS%20P302%20T10"
    }
  },
  "meta": { "timestamp": "2026-10-01T09:10:00Z" },
  "error": null
}
```

---

## 4. Hướng Dẫn Frontend Tích Hợp (Frontend Integration Rules)

1. **Khởi tạo Axios Client (`src/services/apiClient.ts`):**
   - Đính kèm tự động Interceptor thêm `Authorization: Bearer <token>`.
   - Bắt các lỗi `401 Unauthorized` để tự động kích hoạt Refresh Token flow hoặc chuyển hướng về `/login`.
2. **Xử lý TypeScript DTOs (`src/types/api.ts`):**
   - Mọi interface phải kế thừa từ `ApiResponse<T>` chuẩn hóa.
3. **Tuân thủ Anti-AI-Slop UI:**
   - 100% components kết nối API phải xử lý đủ 5 trạng thái: `idle`, `loading` (Skeleton loader), `success` (dữ liệu thật), `error` (thông báo lỗi thân thiện từ `error.message`), `empty` (thông báo không có dữ liệu khi danh sách rỗng).


## 5. Endpoints Tự Động Đồng Bộ Từ Backend Code

#### `GET` /api/v1/invoices
- **Tên hàm Backend:** `get_all_invoices()` (tại `billing.py:50`)
- **Mô tả:** Chủ nhà/Admin xem danh sách tất cả hóa đơn theo bộ lọc.
- **Quyền truy cập:** `Landlord`
- **Phương thức hỗ trợ:** `GET`

- **Response Chuẩn:**
```json
{
  "success": true,
  "data": {},
  "meta": { "timestamp": "2026-10-01T12:00:00Z" },
  "error": null
}
```
---
#### `GET` /api/v1/invoices/<int:invoice_id>
- **Tên hàm Backend:** `get_invoice_detail()` (tại `billing.py:68`)
- **Mô tả:** Lấy thông tin chi tiết một hóa đơn kèm các khoản mục chi tiết.
- **Quyền truy cập:** `Public`
- **Phương thức hỗ trợ:** `GET`
- **Tham số đường dẫn (Path Params):** `invoice_id`

- **Response Chuẩn:**
```json
{
  "success": true,
  "data": {},
  "meta": { "timestamp": "2026-10-01T12:00:00Z" },
  "error": null
}
```
---
#### `POST` /api/v1/<int:invoice_id>/payment-slip
- **Tên hàm Backend:** `upload_payment_slip()` (tại `billing.py:88`)
- **Mô tả:** Khách thuê tải ảnh chụp màn hình biên lai chuyển khoản ngân hàng.
- **Quyền truy cập:** `Public`
- **Phương thức hỗ trợ:** `POST`
- **Tham số đường dẫn (Path Params):** `invoice_id`

**Chi tiết nghiệp vụ:**
```text
Form-data:
    slip_image: File ảnh biên lai
```

- **Response Chuẩn:**
```json
{
  "success": true,
  "data": {},
  "meta": { "timestamp": "2026-10-01T12:00:00Z" },
  "error": null
}
```
---
#### `POST` /api/v1/invoices/<int:invoice_id>/confirm-payment
- **Tên hàm Backend:** `confirm_invoice_payment()` (tại `billing.py:113`)
- **Mô tả:** Chủ nhà/Admin xác nhận đối soát biên lai thành công và đánh dấu đã thanh toán.
- **Quyền truy cập:** `Landlord`
- **Phương thức hỗ trợ:** `POST`
- **Tham số đường dẫn (Path Params):** `invoice_id`

- **Response Chuẩn:**
```json
{
  "success": true,
  "data": {},
  "meta": { "timestamp": "2026-10-01T12:00:00Z" },
  "error": null
}
```
---
#### `GET` /api/v1/rooms/<int:room_id>/roommates
- **Tên hàm Backend:** `list_roommates()` (tại `roommates.py:21`)
- **Mô tả:** GET /api/v1/rooms/:room_id/roommates
- **Quyền truy cập:** `Public`
- **Phương thức hỗ trợ:** `GET`
- **Tham số đường dẫn (Path Params):** `room_id`

**Chi tiết nghiệp vụ:**
```text
Lấy danh sách người ở cùng trong phòng.
- Khách thuê chỉ xem được phòng của mình.
- Landlord/Admin xem được mọi phòng.
```

- **Response Chuẩn:**
```json
{
  "success": true,
  "data": {},
  "meta": { "timestamp": "2026-10-01T12:00:00Z" },
  "error": null
}
```
---
#### `POST` /api/v1/rooms/<int:room_id>/roommates
- **Tên hàm Backend:** `add_roommate()` (tại `roommates.py:48`)
- **Mô tả:** POST /api/v1/rooms/:room_id/roommates
- **Quyền truy cập:** `Public`
- **Phương thức hỗ trợ:** `POST`
- **Tham số đường dẫn (Path Params):** `room_id`

**Chi tiết nghiệp vụ:**
```text
Thêm người ở cùng vào phòng.
- Tenant: chỉ thêm vào phòng mình đang ở.
- Landlord/Admin: thêm vào bất kỳ phòng nào.
```

- **Response Chuẩn:**
```json
{
  "success": true,
  "data": {},
  "meta": { "timestamp": "2026-10-01T12:00:00Z" },
  "error": null
}
```
---
#### `PATCH` /api/v1/roommates/<int:roommate_id>/status
- **Tên hàm Backend:** `update_residence_status()` (tại `roommates.py:104`)
- **Mô tả:** PATCH /api/v1/roommates/:id/status
- **Quyền truy cập:** `Landlord`
- **Phương thức hỗ trợ:** `PATCH`
- **Tham số đường dẫn (Path Params):** `roommate_id`

**Chi tiết nghiệp vụ:**
```text
Cập nhật trạng thái đăng ký tạm trú (chỉ landlord/admin).
Body: { "status": "registered" | "rejected" | "pending" }
```

- **Response Chuẩn:**
```json
{
  "success": true,
  "data": {},
  "meta": { "timestamp": "2026-10-01T12:00:00Z" },
  "error": null
}
```
---
#### `GET` /api/v1/<int:room_id>
- **Tên hàm Backend:** `get_room_detail()` (tại `rooms.py:94`)
- **Mô tả:** GET /api/v1/rooms/:id
- **Quyền truy cập:** `Public`
- **Phương thức hỗ trợ:** `GET`
- **Tham số đường dẫn (Path Params):** `room_id`

**Chi tiết nghiệp vụ:**
```text
Lấy chi tiết một phòng. Yêu cầu JWT.
```

- **Response Chuẩn:**
```json
{
  "success": true,
  "data": {},
  "meta": { "timestamp": "2026-10-01T12:00:00Z" },
  "error": null
}
```
---
#### `PUT` /api/v1/<int:ticket_id>/status
- **Tên hàm Backend:** `update_ticket_status()` (tại `tickets.py:126`)
- **Mô tả:** Chủ nhà/Admin cập nhật trạng thái xử lý ticket (in_progress, resolved, cancelled).
- **Quyền truy cập:** `Landlord`
- **Phương thức hỗ trợ:** `PUT`
- **Tham số đường dẫn (Path Params):** `ticket_id`

- **Response Chuẩn:**
```json
{
  "success": true,
  "data": {},
  "meta": { "timestamp": "2026-10-01T12:00:00Z" },
  "error": null
}
```
---
#### `GET` /api/v1/<int:violation_id>
- **Tên hàm Backend:** `get_violation_detail()` (tại `violations.py:138`)
- **Mô tả:** Lấy chi tiết biên bản vi phạm theo ID.
- **Quyền truy cập:** `Public`
- **Phương thức hỗ trợ:** `GET`
- **Tham số đường dẫn (Path Params):** `violation_id`

- **Response Chuẩn:**
```json
{
  "success": true,
  "data": {},
  "meta": { "timestamp": "2026-10-01T12:00:00Z" },
  "error": null
}
```
---
#### `PUT` /api/v1/<int:violation_id>/acknowledge
- **Tên hàm Backend:** `acknowledge_violation()` (tại `violations.py:148`)
- **Mô tả:** Khách thuê xác nhận đã đọc thông báo nhắc nhở/cảnh cáo vi phạm.
- **Quyền truy cập:** `Public`
- **Phương thức hỗ trợ:** `PUT`
- **Tham số đường dẫn (Path Params):** `violation_id`

- **Response Chuẩn:**
```json
{
  "success": true,
  "data": {},
  "meta": { "timestamp": "2026-10-01T12:00:00Z" },
  "error": null
}
```
---
#### `PUT` /api/v1/<int:violation_id>/resolve
- **Tên hàm Backend:** `resolve_violation()` (tại `violations.py:164`)
- **Mô tả:** Chủ nhà/Admin đóng biên bản vi phạm khi đã giải quyết xong.
- **Quyền truy cập:** `Landlord`
- **Phương thức hỗ trợ:** `PUT`
- **Tham số đường dẫn (Path Params):** `violation_id`

- **Response Chuẩn:**
```json
{
  "success": true,
  "data": {},
  "meta": { "timestamp": "2026-10-01T12:00:00Z" },
  "error": null
}
```
---


## 5. Endpoints Tự Động Đồng Bộ Từ Backend Code

#### `GET` /api/v1/<int:contract_id>
- **Tên hàm Backend:** `get_contract_detail()` (tại `contracts.py:54`)
- **Mô tả:** Xem thông tin chi tiết một hợp đồng.
- **Quyền truy cập:** `Public`
- **Phương thức hỗ trợ:** `GET`
- **Tham số đường dẫn (Path Params):** `contract_id`

- **Response Chuẩn:**
```json
{
  "success": true,
  "data": {},
  "meta": { "timestamp": "2026-10-01T12:00:00Z" },
  "error": null
}
```
---
#### `GET` /api/v1/<int:contract_id>/refund-preview
- **Tên hàm Backend:** `preview_refund()` (tại `contracts.py:129`)
- **Mô tả:** Tính toán bản dự toán quyết toán hoàn cọc khi trả phòng.
- **Quyền truy cập:** `Landlord`
- **Phương thức hỗ trợ:** `GET`
- **Tham số đường dẫn (Path Params):** `contract_id`

- **Response Chuẩn:**
```json
{
  "success": true,
  "data": {},
  "meta": { "timestamp": "2026-10-01T12:00:00Z" },
  "error": null
}
```
---
#### `POST` /api/v1/<int:contract_id>/settle-refund
- **Tên hàm Backend:** `settle_refund()` (tại `contracts.py:150`)
- **Mô tả:** Nghiệm thu hoàn tất trả phòng, thanh lý hợp đồng và cấn trừ hoàn cọc.
- **Quyền truy cập:** `Landlord`
- **Phương thức hỗ trợ:** `POST`
- **Tham số đường dẫn (Path Params):** `contract_id`

- **Response Chuẩn:**
```json
{
  "success": true,
  "data": {},
  "meta": { "timestamp": "2026-10-01T12:00:00Z" },
  "error": null
}
```
---
#### `GET` /api/v1/summary
- **Tên hàm Backend:** `get_financial_summary()` (tại `expenses.py:99`)
- **Mô tả:** Lấy báo cáo tổng hợp Doanh thu - Chi phí OpEx - Lợi nhuận Ròng theo tháng/năm.
- **Quyền truy cập:** `Landlord`
- **Phương thức hỗ trợ:** `GET`

- **Response Chuẩn:**
```json
{
  "success": true,
  "data": {},
  "meta": { "timestamp": "2026-10-01T12:00:00Z" },
  "error": null
}
```
---


## 5. Endpoints Tự Động Đồng Bộ Từ Backend Code

#### `POST` /api/v1/register/send-otp
- **Tên hàm Backend:** `send_register_otp()` (tại `auth.py:17`)
- **Mô tả:** POST /api/v1/auth/register/send-otp
- **Quyền truy cập:** `Public`
- **Phương thức hỗ trợ:** `POST`

**Chi tiết nghiệp vụ:**
```text
Gửi mã OTP 6 số qua email để xác thực đăng ký tài khoản.
Public endpoint.
```

- **Response Chuẩn:**
```json
{
  "success": true,
  "data": {},
  "meta": { "timestamp": "2026-10-01T12:00:00Z" },
  "error": null
}
```
---
#### `POST` /api/v1/forgot-password
- **Tên hàm Backend:** `forgot_password()` (tại `auth.py:103`)
- **Mô tả:** POST /api/v1/auth/forgot-password
- **Quyền truy cập:** `Public`
- **Phương thức hỗ trợ:** `POST`

**Chi tiết nghiệp vụ:**
```text
Gửi mã OTP đặt lại mật khẩu qua email.
Public endpoint.
```

- **Response Chuẩn:**
```json
{
  "success": true,
  "data": {},
  "meta": { "timestamp": "2026-10-01T12:00:00Z" },
  "error": null
}
```
---
#### `POST` /api/v1/reset-password
- **Tên hàm Backend:** `reset_password()` (tại `auth.py:131`)
- **Mô tả:** POST /api/v1/auth/reset-password
- **Quyền truy cập:** `Public`
- **Phương thức hỗ trợ:** `POST`

**Chi tiết nghiệp vụ:**
```text
Xác minh mã OTP và cập nhật mật khẩu mới.
Public endpoint.
```

- **Response Chuẩn:**
```json
{
  "success": true,
  "data": {},
  "meta": { "timestamp": "2026-10-01T12:00:00Z" },
  "error": null
}
```
---


## 5. Endpoints Tự Động Đồng Bộ Từ Backend Code

#### `GET` /api/v1/buildings
- **Tên hàm Backend:** `list_buildings()` (tại `rooms.py:144`)
- **Mô tả:** GET /api/v1/rooms/buildings
- **Quyền truy cập:** `Public`
- **Phương thức hỗ trợ:** `GET`

**Chi tiết nghiệp vụ:**
```text
Lấy danh sách các tòa nhà căn hộ đang quản lý.
```

- **Response Chuẩn:**
```json
{
  "success": true,
  "data": {},
  "meta": { "timestamp": "2026-10-01T12:00:00Z" },
  "error": null
}
```
---
#### `PATCH` /api/v1/<int:room_id>/status
- **Tên hàm Backend:** `patch_room_status()` (tại `rooms.py:242`)
- **Mô tả:** PATCH /api/v1/rooms/:room_id/status
- **Quyền truy cập:** `Landlord`
- **Phương thức hỗ trợ:** `PATCH`
- **Tham số đường dẫn (Path Params):** `room_id`

**Chi tiết nghiệp vụ:**
```text
Đổi nhanh trạng thái phòng (vacant, occupied, maintenance).
```

- **Response Chuẩn:**
```json
{
  "success": true,
  "data": {},
  "meta": { "timestamp": "2026-10-01T12:00:00Z" },
  "error": null
}
```
---
