# BẢN ĐẶC TẢ YÊU CẦU PHẦN MỀM (SOFTWARE REQUIREMENTS SPECIFICATION - SRS)
**Tên dự án:** Hệ thống Quản lý Căn hộ Cho thuê Tích hợp Trí tuệ Nhân tạo (Smart Apartment Management System - SAMS)  
**Tài liệu:** SRS.md (Engineering & AI Implementation Reference)  
**Phiên bản:** 1.0.0  
**Ngày ban hành:** 01/10/2026  
**Phương pháp thiết kế:** ISO/IEC/IEEE 29148 Standard, Clean Architecture, Repository Pattern, 12-Factor App  
**Nhân sự thực hiện:**  
- **Phùng Thiên Trường:** Lead Backend & AI Protocol Engineer  
- **Đinh Hoàng An:** Fullstack UI/UX & DevOps Engineer  

---

## MỤC LỤC
1. [GIỚI THIỆU TỔNG QUAN (INTRODUCTION)](#1-giới-thiệu-tổng-quan-introduction)
2. [MÔ TẢ TỔNG QUAN HỆ THỐNG (OVERALL DESCRIPTION)](#2-mô-tả-tổng-quan-hệ-thống-overall-description)
3. [ĐẶC TẢ BIẾN MÔI TRƯỜNG TOÀN HỆ THỐNG (.ENV SPECIFICATION)](#3-đặc-tả-biến-môi-trường-toàn-hệ-thống-env-specification)
4. [YÊU CẦU TÍNH NĂNG CHI TIẾT (SYSTEM FEATURES & FUNCTIONAL REQUIREMENTS)](#4-yêu-cầu-tính-năng-chi-tiết-system-features--functional-requirements)
   - [4.1. Phân hệ Khách thuê (Tenant Subsystem)](#41-phân-hệ-khách-thuê-tenant-subsystem)
   - [4.2. Phân hệ Chủ căn hộ & Quản lý (Landlord Subsystem)](#42-phân-hệ-chủ-căn-hộ--quản-lý-landlord-subsystem)
   - [4.3. Phân hệ Quản trị & Xác thực (Auth & RBAC Subsystem)](#43-phân-hệ-quản-trị--xác-thực-auth--rbac-subsystem)
5. [ĐẶC TẢ CƠ SỞ DỮ LIỆU & LƯỢC ĐỒ (DATABASE SCHEMA SPECIFICATION)](#5-đặc-tả-cơ-sở-dữ-liệu--lược-đồ-database-schema-specification)
6. [ĐẶC TẢ GIAO DIỆN API & GIAO THỨC (API & PROTOCOL SPECIFICATIONS)](#6-đặc-tả-giao-diện-api--giao-thức-api--protocol-specifications)
   - [6.1. RESTful API Endpoints](#61-restful-api-endpoints)
   - [6.2. Model Context Protocol (MCP) Server Specification](#62-model-context-protocol-mcp-server-specification)
   - [6.3. Gemini API Integration Specification (LLM & Vision)](#63-gemini-api-integration-specification-llm--vision)
7. [YÊU CẦU PHI CHỨC NĂNG (NON-FUNCTIONAL REQUIREMENTS - NFRS)](#7-yêu-cầu-phi-chức-năng-non-functional-requirements---nfrs)
8. [MA TRẬN TRUY VẾT & QUY TẮC MÃ HÓA CHO AI (AI CODING GUIDELINES)](#8-ma-trận-truy-vết--quy-tắc-mã-hóa-cho-ai-ai-coding-guidelines)

---

## 1. GIỚI THIỆU TỔNG QUAN (INTRODUCTION)

### 1.1. Mục đích tài liệu
Tài liệu Đặc tả Yêu cầu Phần mềm (SRS) này đóng vai trò là **kim chỉ nam kỹ thuật chuẩn xác và duy nhất** cho toàn bộ vòng đời phát triển dự án SAMS. Tài liệu này cung cấp định nghĩa chi tiết về kiến trúc dữ liệu, các hàm API, luồng xử lý AI, định dạng giao tiếp MCP và các quy tắc kiểm thử, nhằm giúp lập trình viên và các AI Coding Assistant tuân thủ nghiêm ngặt, **tuyệt đối không đi lạc hướng, không phát sinh tính năng rác hay các thiết kế vô lý**.

### 1.2. Phạm vi sản phẩm (Product Scope)
SAMS là giải pháp chuyển đổi số toàn diện cho mô hình căn hộ dịch vụ, nhà trọ và chung cư mini cho thuê. Hệ thống kết hợp:
- **Cốt lõi nghiệp vụ vận hành thực tế:** Quản lý phòng, hợp đồng, tính tiền điện nước, xuất hóa đơn VietQR động, ghi nhận chi phí vận hành (OpEx), kiểm kê tài sản nhận phòng và quyết toán hoàn cọc khi trả phòng.
- **Trí tuệ nhân tạo phía Khách thuê:** Sử dụng **Google Gemini API** (Gemini 1.5/2.0 Flash) cung cấp Trợ lý ảo đàm thoại 24/7 (tra cứu nội quy, hóa đơn, gửi ticket sửa chữa qua Function Calling) và **Gemini Vision OCR** đọc công tơ điện nước tự động từ ảnh chụp.
- **Trí tuệ nhân tạo phía Chủ căn hộ:** Xây dựng **MCP Server** theo chuẩn mở Model Context Protocol, cung cấp 7 công cụ phân tích dữ liệu thời gian thực để chủ nhà ra lệnh cho các LLM Host (Claude Desktop, Cursor, Custom Agent) xuất báo cáo điều hành.

### 1.3. Định nghĩa & Thuật ngữ viết tắt
- **SAMS:** Smart Apartment Management System (Hệ thống Quản lý Căn hộ Thông minh).
- **Tenant:** Khách thuê căn hộ.
- **Landlord:** Chủ sở hữu căn hộ hoặc Quản lý tòa nhà.
- **MCP:** Model Context Protocol - Giao thức chuẩn hóa của Anthropic cho phép các LLM truy cập dữ liệu và gọi công cụ an toàn.
- **FastMCP:** Thư viện Python cấp cao triển khai máy chủ MCP.
- **WAL Mode:** Write-Ahead Logging - Chế độ ghi nhật ký trước của SQLite cho phép đọc song song không chặn.
- **OpEx:** Operating Expenses - Chi phí vận hành tòa nhà (điện chung, nước chung, internet, rác, sửa chữa).
- **VietQR:** Tiêu chuẩn thanh toán chuyển khoản liên ngân hàng tự động của Việt Nam theo chuẩn quốc tế EMVCo.

---

## 2. MÔ TẢ TỔNG QUAN HỆ THỐNG (OVERALL DESCRIPTION)

### 2.1. Phối cảnh sản phẩm & Kiến trúc môi trường
Hệ thống được đóng gói 100% trong môi trường container hóa thông qua **Docker Compose**, bao gồm 4 containers độc lập chạy trên mạng nội bộ `sams_network`:
1. **`sams_nginx` (Alpine):** Reverse Proxy, SSL Termination, nén Gzip, phục vụ Frontend tĩnh và điều hướng:
   - `/` $\rightarrow$ React SPA
   - `/api/v1/*` $\rightarrow$ Flask Backend (`sams_backend:5000`)
   - `/mcp/*` $\rightarrow$ FastMCP Server (`sams_mcp:8000`)
2. **`sams_backend` (Python 3.12 Flask):** Xử lý nghiệp vụ RESTful API, xác thực JWT, kết nối Gemini API.
3. **`sams_mcp` (Python 3.12 FastMCP):** Cung cấp các công cụ MCP truy vấn dữ liệu thống kê cho LLM Host.
4. **Volume `sams_sqlite_data`:** Named Volume gắn vào cả 2 container backend để chia sẻ file `apartment.db` an toàn ở chế độ WAL.

```
                    ┌─────────────────────────┐
                    │ Client Browser / Mobile │
                    └────────────┬────────────┘
                                 │ :80 / :443
                    ┌────────────▼────────────┐
                    │   Nginx Reverse Proxy   │
                    └──────┬───────────┬──────┘
             /api/v1/*     │           │  /mcp/* (SSE)
     ┌─────────────────────▼─┐       ┌─▼─────────────────────┐
     │  Flask Backend API    │       │   FastMCP Server      │
     │  (Port 5000)          │       │   (Port 8000)         │
     └──────────┬────────────┘       └─────────┬─────────────┘
                │ Đọc/Ghi                      │ Đọc thống kê
                ▼                              ▼
     ┌───────────────────────────────────────────────────────┐
     │  SQLite Database Engine (apartment.db - WAL Mode)     │
     │  Docker Volume: sams_sqlite_data                      │
     └───────────────────────────────────────────────────────┘
```

### 2.2. Phân loại Người dùng & Quyền hạn (User Classes)
1. **Khách thuê (Tenant - Role: `tenant`):**
   - Chỉ xem thông tin phòng của chính mình, hợp đồng hiện tại, các hóa đơn cần thanh toán.
   - Chụp ảnh công tơ điện nước phòng mình để hệ thống OCR chốt số.
   - Quét mã VietQR thanh toán tiền phòng.
   - Xác nhận bảng kiểm kê đồ đạc khi dọn vào phòng.
   - Nhắn tin đàm thoại với Trợ lý ảo Gemini, gửi ticket báo hỏng và xem thông báo bảng tin.
2. **Chủ căn hộ / Quản lý (Landlord - Role: `landlord`):**
   - Toàn quyền quản trị danh sách tòa nhà, phòng, khách thuê, hợp đồng.
   - Duyệt/chốt số điện nước hàng tháng, xuất hóa đơn hàng loạt.
   - Ghi nhận chi phí vận hành OpEx, xem biểu đồ Lợi nhuận ròng.
   - Nghiệm thu trả phòng và xuất biên bản quyết toán hoàn cọc.
   - Kết nối LLM Host (Claude Desktop/Cursor) với MCP Server để truy vấn dữ liệu kinh doanh.
3. **Quản trị viên Hệ thống (Admin - Role: `admin`):**
   - Quản lý tài khoản người dùng, phân quyền, cấu hình hệ thống, sao lưu database.

---

## 3. ĐẶC TẢ BIẾN MÔI TRƯỜNG TOÀN HỆ THỐNG (.ENV SPECIFICATION)

Toàn bộ hệ thống được kiểm soát và cấu hình tập trung qua file `.env`. Tuyệt đối không hard-code các thông số nhạy cảm trong mã nguồn:

```ini
# ==============================================================================
# SMART APARTMENT MANAGEMENT SYSTEM (SAMS) - ENVIRONMENT CONFIGURATION
# ==============================================================================

# --- MÔI TRƯỜNG & CHUNG ---
ENVIRONMENT=development                     # development | production | testing
SECRET_KEY=sams_super_secret_jwt_key_2026_xyz987654321
TIMEZONE=Asia/Ho_Chi_Minh

# --- FLASK BACKEND CONFIGURATION ---
FLASK_APP=wsgi.py
FLASK_DEBUG=1                               # 0 trên Production
FLASK_RUN_HOST=0.0.0.0
FLASK_RUN_PORT=5000
JWT_ACCESS_TOKEN_EXPIRES_MINUTES=1440       # 24 giờ
JWT_REFRESH_TOKEN_EXPIRES_DAYS=30
CORS_ORIGINS=http://localhost:3000,http://localhost:80,http://127.0.0.1

# --- SQLITE DATABASE CONFIGURATION (WAL CONCURRENCY) ---
SQLITE_DB_PATH=/app/instance/apartment.db
SQLITE_BUSY_TIMEOUT_MS=30000                # 30 giây chờ khóa ghi
SQLITE_CACHE_SIZE_KB=64000                  # 64MB In-memory cache

# --- GOOGLE GEMINI AI CONFIGURATION ---
GEMINI_API_KEY=AIzaSyYourGeminiApiKeyHere123456789
GEMINI_TEXT_MODEL=gemini-1.5-flash          # Model xử lý chat & function calling
GEMINI_VISION_MODEL=gemini-1.5-flash        # Model xử lý OCR ảnh công tơ điện nước
GEMINI_TEMPERATURE=0.2                      # Nhiệt độ thấp cho độ chính xác dữ liệu cao

# --- VIETQR PAYMENT CONFIGURATION (CHUẨN NAPAS247) ---
VIETQR_BANK_BIN=970422                      # Mã BIN ngân hàng (VD: 970422 = MBBank)
VIETQR_BANK_NAME=MBBank
VIETQR_ACCOUNT_NUMBER=0987654321            # Số tài khoản thụ hưởng của Chủ nhà
VIETQR_ACCOUNT_NAME=NGUYEN VAN CHU NHA      # Tên chủ tài khoản (Viết hoa không dấu)
VIETQR_TEMPLATE=compact2                    # compact | compact2 | qr_only

# --- ĐƠN GIÁ ĐIỆN NƯỚC MẶC ĐỊNH (VNĐ) ---
DEFAULT_ELECTRICITY_PRICE_PER_KWH=3500      # 3.500đ / kWh
DEFAULT_WATER_PRICE_PER_M3=25000            # 25.000đ / m3 (hoặc tính theo đầu người)
DEFAULT_INTERNET_FEE_PER_ROOM=100000        # 100.000đ / phòng
DEFAULT_CLEANING_FEE_PER_ROOM=50000         # 50.000đ / phòng

# --- MODEL CONTEXT PROTOCOL (MCP) SERVER CONFIGURATION ---
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8000
MCP_SERVER_AUTH_TOKEN=mcp_secret_token_landlord_2026_secure
MCP_TRANSPORT=sse                           # sse | stdio

# --- UPLOAD & MEDIA STORAGE ---
UPLOAD_FOLDER=/app/uploads
MAX_CONTENT_LENGTH_MB=10                    # Giới hạn ảnh chụp tối đa 10MB
ALLOWED_EXTENSIONS=png,jpg,jpeg,webp
```

---

## 4. YÊU CẦU TÍNH NĂNG CHI TIẾT (SYSTEM FEATURES & FUNCTIONAL REQUIREMENTS)

### 4.1. Phân hệ Khách thuê (Tenant Subsystem)

#### FR-TENANT-01: Tra cứu & Đàm thoại Trợ lý ảo AI 24/7 (Gemini Function Calling)
- **Mục tiêu:** Cho phép khách thuê đặt câu hỏi tự nhiên bằng tiếng Việt về tiền phòng, hợp đồng, nội quy và tiếp nhận báo hỏng hóc.
- **Tác nhân:** Khách thuê (`tenant`).
- **Luồng xử lý:**
  1. Khách gửi tin nhắn từ giao diện Chatbot: *"Tháng này phòng tôi hết bao nhiêu tiền điện?"*.
  2. Backend nạp `Tenant Context`: Xác định `user_id`, `room_id = 302`, họ tên khách và nạp nội quy chung cư vào `System Instruction`.
  3. Backend khai báo bộ Tools cho Gemini SDK:
     - `get_unpaid_invoices(room_id)`
     - `get_room_contract_info(room_id)`
     - `create_maintenance_ticket(category, description, priority)`
  4. Gemini nhận diện ý định hỏi tiền điện, tự động trả về lệnh gọi hàm `get_unpaid_invoices(room_id=302)`.
  5. Backend thực thi truy vấn SQLite, trả về số liệu thực (Chỉ số: 85 kWh, Thành tiền: 297.500đ, Tổng hóa đơn: 3.797.500đ).
  6. Gemini tổng hợp câu trả lời tự nhiên, thân thiện và trả về qua giao diện Streaming text.
- **Ràng buộc:** Khách thuê phòng 302 tuyệt đối không được xem dữ liệu của phòng 301. Dữ liệu nạp vào Function Call phải được lọc cố định theo `tenant_id` lấy từ JWT Token.

#### FR-TENANT-02: Chụp ảnh Chốt số Điện - Nước bằng AI (Gemini Vision OCR)
- **Mục tiêu:** Tự động hóa quá trình ghi số điện nước hàng tháng, loại bỏ việc nhập tay sai lệch.
- **Tác nhân:** Khách thuê (`tenant`).
- **Input:** Ảnh chụp trực tiếp đồng hồ công tơ (điện hoặc nước) từ camera điện thoại, loại công tơ (`electricity` hoặc `water`).
- **Luồng xử lý:**
  1. Khách bấm nút "Chốt số điện/nước", chụp ảnh công tơ phòng mình và gửi lên.
  2. Backend kiểm tra file ảnh hợp lệ (dung lượng $\le 10MB$, đuôi ảnh hợp lệ), lưu ảnh vào thư mục `/uploads/meters/`.
  3. Backend gọi **Gemini 1.5 Flash Vision** kèm System Prompt chuyên dụng:
     > *"Bạn là chuyên gia thẩm định công tơ điện nước. Hãy đọc dãy số hiển thị trên mặt đồng hồ công tơ trong ảnh. Chỉ trả về định dạng JSON thuần: { 'reading': float, 'confidence': float, 'meter_type': 'electricity'|'water' }."*
  4. Hệ thống phân tích kết quả JSON trả về.
  5. Truy vấn `UtilityReadingRepository` để lấy chỉ số tháng liền trước: $Reading_{old}$.
  6. **Kiểm tra nghiệp vụ (Business Rule):**
     - Nếu $Reading_{new} < Reading_{old}$: Báo cảnh báo "Chỉ số mới nhỏ hơn chỉ số cũ, vui lòng kiểm tra lại ảnh chụp".
     - Nếu $Reading_{new} - Reading_{old} > 500$ kWh (đột biến bất thường): Đánh dấu cờ `flag_abnormal = True` để chủ nhà phúc tra.
  7. Hiển thị số đọc được lên giao diện màn hình để khách xác nhận "Đồng ý chốt số".
  8. Lưu bản ghi vào bảng `utility_readings` kèm đường link ảnh gốc.

#### FR-TENANT-03: Thanh toán Hóa đơn bằng VietQR Động
- **Mục tiêu:** Giúp khách thuê thanh toán chuyển khoản chính xác 100% trong 5 giây, không cần gõ số tiền hay nội dung.
- **Tác nhân:** Khách thuê (`tenant`).
- **Luồng xử lý:**
  1. Khi mở chi tiết hóa đơn (trạng thái `unpaid`), hệ thống gọi `VietQRService` sinh payload mã QR theo chuẩn Napas247:
     - Số tài khoản: Cấu hình từ `.env` (`VIETQR_ACCOUNT_NUMBER`).
     - Ngân hàng: Cấu hình từ `.env` (`VIETQR_BANK_BIN`).
     - Số tiền: Tổng tiền hóa đơn `invoices.total_amount`.
     - Cú pháp nội dung: `SAMS P[room_number] T[month]` (Ví dụ: `SAMS P302 T10`).
  2. Giao diện hiển thị ảnh VietQR động khổ lớn, kèm nút "Tải mã QR" hoặc "Mở ứng dụng ngân hàng".
  3. Khách quét mã, app ngân hàng tự động điền đầy đủ thông tin. Khách bấm chuyển tiền.
  4. Khách có thể bấm nút "Đã thanh toán" kèm ảnh chụp màn hình chuyển khoản để chủ nhà đối soát nhanh.

#### FR-TENANT-04: Kiểm kê Tài sản khi Nhận phòng (Digital Move-in Checklist)
- **Mục tiêu:** Bảo vệ quyền lợi tiền cọc của khách thuê, minh bạch hiện trạng đồ đạc khi mới dọn vào.
- **Tác nhân:** Khách thuê (`tenant`).
- **Luồng xử lý:**
  1. Khi hợp đồng mới được kích hoạt, giao diện của khách hiển thị thông báo "Kiểm kê nhận phòng".
  2. Danh sách thiết bị mặc định trong phòng hiển thị (ví dụ: Điều hòa Daikin, Giường 1m8, Nệm Kymdan, Tủ lạnh Panasonic 180L, Remote TV, Chìa khóa cửa).
  3. Khách thuê kiểm tra từng món, chọn trạng thái (Tốt / Trầy xước / Hư hỏng), đính kèm ảnh chụp hiện trạng (nếu có lỗi).
  4. Khách bấm "Xác nhận nhận phòng". Hệ thống khóa trạng thái và lưu thời gian `verified_at`.

#### FR-TENANT-05: Bảng tin Tòa nhà & Tiếp nhận Báo hỏng (Service Tickets)
- **Mục tiêu:** Cập nhật thông tin vận hành từ chủ nhà và gửi yêu cầu sửa chữa tức thì.
- **Tác nhân:** Khách thuê (`tenant`).
- **Nghiệp vụ:**
  - Xem danh sách thông báo mới nhất (Cắt nước bảo trì, Phun thuốc côn trùng, Đóng cổng an ninh).
  - Gửi yêu cầu sửa chữa: Chọn danh mục (Điện / Nước / Đồ gỗ / Khác), mô tả chi tiết, tải ảnh hiện trường, chọn mức độ khẩn cấp (Thường / Gấp).
  - Theo dõi tiến độ: `Chờ xử lý` $\rightarrow$ `Đang sửa chữa` $\rightarrow$ `Đã hoàn thành`.

#### FR-TENANT-06: Tìm kiếm & Tra cứu Phòng trống (Apartment Search & Filter)
- **Mục tiêu:** Giúp khách thuê tiềm năng hoặc khách vãng lai tìm kiếm phòng phù hợp với nhu cầu.
- **Tác nhân:** Khách thuê (`tenant`), Khách vãng lai (`public`).
- **Nghiệp vụ:**
  - Lọc theo khoảng giá thuê (`min_price`, `max_price`), diện tích phòng (`min_area`, `max_area`), tầng lầu.
  - Lọc theo tiện ích đi kèm (Có ban công, máy giặt riêng, bếp nấu ăn, bãi đỗ ô tô).
  - Chỉ hiển thị các phòng có trạng thái `status = 'vacant'`.
  - Hiển thị danh sách ảnh phòng, giá thuê cơ bản, tiền cọc quy định và địa chỉ tòa nhà.

#### FR-TENANT-07: Quản lý Căn hộ Đang thuê & Khai báo Bạn cùng phòng (My Room & Roommates Management)
- **Mục tiêu:** Giúp khách đại diện quản lý hợp đồng căn hộ và chủ động đăng ký thông tin người ở cùng để khai báo tạm trú công an theo luật cư trú.
- **Tác nhân:** Khách thuê đại diện hợp đồng (`tenant`).
- **Nghiệp vụ:**
  - Xem thông tin phòng đang thuê: Mã phòng, diện tích, ngày bắt đầu thuê, thời hạn hợp đồng, số tiền cọc đang giữ.
  - Xem danh sách thành viên đang cùng ở trong phòng (`roommates`).
  - Thêm thành viên mới ở cùng: Họ và tên, số điện thoại, số CCCD/CMND (bắt buộc để khai báo tạm trú), ngày tháng năm sinh, quê quán, biển số xe máy.
  - Theo dõi trạng thái tạm trú của từng thành viên: `pending` (chờ khai báo), `registered` (đã đăng ký công an phường), `rejected` (thiếu giấy tờ).

#### FR-TENANT-08: Thanh toán Trực tuyến Đa kênh (Online Payment Options)
- **Mục tiêu:** Đa dạng hóa phương thức thanh toán cho khách thuê khi hóa đơn đã được cập nhật trên web.
- **Tác nhân:** Khách thuê (`tenant`).
- **Nghiệp vụ:**
  - **Phương thức 1 - Quét mã VietQR động:** Hệ thống hiển thị mã QR theo chuẩn EMVCo tự điền số tài khoản, số tiền và nội dung chuyển khoản. Khách quét mã bằng App ngân hàng bất kỳ.
  - **Phương thức 2 - Tải biên lai chuyển khoản (Payment Proof Upload):** Nếu khách chuyển khoản qua Internet Banking thông thường hoặc máy ATM, khách có thể tải ảnh chụp màn hình giao dịch chuyển tiền lên web.
  - Trạng thái hóa đơn chuyển sang `pending_verification` để chủ nhà đối soát ngân hàng và xác nhận trong 1 cú nhấp chuột.

---

### 4.2. Phân hệ Chủ căn hộ & Quản lý (Landlord Subsystem)

#### FR-LANDLORD-01: Quản lý Danh mục Phòng & Hợp đồng Cho thuê
- **Mục tiêu:** Quản lý vòng đời phòng ốc và hợp đồng thuê.
- **Nghiệp vụ:**
  - Tạo mới phòng, gán đơn giá cơ bản, diện tích, trang thiết bị đồ đạc (`room_assets`).
  - Lập hợp đồng thuê: Chọn phòng, chọn khách thuê, ngày bắt đầu, ngày kết thúc, tiền cọc (`deposit_amount`), tiền thuê hàng tháng (`monthly_rent`).
  - Cập nhật trạng thái phòng tự động: `vacant` (trống) $\leftrightarrow$ `occupied` (đã thuê) $\leftrightarrow$ `maintenance` (đang bảo trì).

#### FR-LANDLORD-02: Tính Tiền Tự động & Quản lý Hóa đơn Hàng tháng
- **Mục tiêu:** Tự động tổng hợp chỉ số điện, nước, phí cố định để xuất hóa đơn trong 1 cú nhấp chuột.
- **Luồng xử lý:**
  1. Hàng tháng, chủ nhà bấm "Xuất hóa đơn toàn tòa nhà".
  2. Backend quét toàn bộ phòng đang có hợp đồng `active`:
     - Tiền phòng cố định = `contracts.monthly_rent`.
     - Tiền điện = $(Reading_{dien\_moi} - Reading_{dien\_cu}) \times DEFAULT\_ELECTRICITY\_PRICE\_PER\_KWH$.
     - Tiền nước = $(Reading_{nuoc\_moi} - Reading_{nuoc\_cu}) \times DEFAULT\_WATER\_PRICE\_PER\_M3$.
     - Tiền dịch vụ cố định (rác, internet, dọn dẹp).
     - Tiền phạt vi phạm nội quy (nếu có trong kỳ tính tiền) từ bảng `room_violations`.
  3. Tạo bản ghi `invoices` và chi tiết `invoice_items`.
  4. Sinh chuỗi `vietqr_payload` cho từng hóa đơn.
  5. Đánh dấu trạng thái `unpaid` và kích hoạt thông báo đến tài khoản khách thuê.

#### FR-LANDLORD-03: Quản lý Chi phí Vận hành (OpEx) & Báo cáo Lợi nhuận Ròng (Net Profit)
- **Mục tiêu:** Quản lý dòng tiền thực tế của bất động sản, phân biệt rõ doanh thu gộp và lợi nhuận ròng.
- **Nghiệp vụ:**
  - Ghi nhận chi phí vận hành: Loại chi phí (`common_electricity` - điện hành lang/thang máy, `water` - nước dùng chung, `internet` - đường truyền tổng, `security` - bảo vệ, `cleaning` - lao công, `maintenance` - bảo dưỡng máy bơm/hạ tầng).
  - Nhập số tiền, ngày chi, đính kèm ảnh hóa đơn/phiếu chi.
  - **Công thức tính toán:**
    $$\text{Doanh thu thực thu} = \sum \text{invoices.total\_amount (trạng thái: paid)}$$
    $$\text{Tổng chi phí vận hành} = \sum \text{expenses.amount}$$
    $$\mathbf{Lợi\ nhuận\ ròng\ (Net\ Profit)} = \text{Doanh thu thực thu} - \text{Tổng chi phí vận hành}$$
  - Trực quan hóa qua biểu đồ cột/đường trên Dashboard (Recharts).

#### FR-LANDLORD-04: Nghiệm thu Trả phòng & Quyết toán Hoàn Tiền Cọc
- **Mục tiêu:** Minh bạch quy trình thanh lý hợp đồng, tự động hóa tính toán trừ cọc để hoàn trả khách.
- **Luồng xử lý:**
  1. Khi khách báo trả phòng, chủ nhà mở biểu mẫu "Nghiệm thu trả phòng".
  2. Hệ thống tải lại bảng tài sản ban đầu (`room_assets`) đã được khách xác nhận lúc nhận phòng.
  3. Chủ nhà kiểm tra thực tế: Nếu có hư hao đồ đạc, nhập chi phí khấu trừ kèm ảnh chứng minh.
  4. Nhập chỉ số điện nước cuối cùng đến ngày trả phòng $\rightarrow$ Hệ thống tự tính tiền điện nước lẻ những ngày cuối.
  5. **Công thức quyết toán cọc:**
    $$\text{Tiền hoàn cọc thực tế} = \text{Tiền cọc gốc} - \text{Tiền điện nước cuối kỳ} - \text{Tổng tiền khấu trừ hư hại} - \text{Các khoản nợ cũ (nếu có)}$$
  6. Xuất biên bản quyết toán định dạng PDF/In ấn có chữ ký xác nhận của hai bên.
  7. Cập nhật trạng thái hợp đồng sang `terminated` và chuyển trạng thái phòng sang `vacant`.

#### FR-LANDLORD-05: Bộ Công cụ Điều hành qua Giao thức MCP (FastMCP Tools)
- **Mục tiêu:** Cung cấp giao diện chuẩn hóa cho các mô hình LLM (Claude Desktop, Cursor) để chủ nhà truy vấn dữ liệu trực tiếp bằng ngôn ngữ tự nhiên.
- **Danh mục 9 Tools chính thức:**
  1. `get_monthly_revenue(month: int, year: int) -> dict`: Thống kê tổng doanh thu hóa đơn đã thanh toán, chưa thanh toán và quá hạn.
  2. `get_net_profit_summary(month: int, year: int) -> dict`: Báo cáo dòng tiền thực tế: Tổng thu, Chi phí OpEx, Lợi nhuận ròng.
  3. `get_debtor_list(grace_period_days: int = 5) -> list`: Liệt kê các phòng quá hạn nộp tiền quá $N$ ngày kèm họ tên, số điện thoại và số tiền nợ.
  4. `get_occupancy_report(building_id: int) -> dict`: Thống kê tỷ lệ lấp đầy, số người ở thực tế theo từng phòng và danh sách người đăng ký tạm trú.
  5. `get_room_violations_summary(room_id: int) -> list`: Tra cứu lịch sử vi phạm, mức độ cảnh cáo và tiền phạt đã xử lý của phòng.
  6. `get_contract_expiration_forecast(days: int = 45) -> list`: Liệt kê các phòng sẽ hết hạn hợp đồng trong $N$ ngày tới để chuẩn bị tìm khách mới.
  7. `get_vacant_rooms() -> list`: Liệt kê các phòng đang trống, diện tích, tầng và giá niêm yết.
  8. `get_pending_tickets() -> list`: Danh sách sự cố bảo trì khách đã báo nhưng chưa được giải quyết xong.
  9. `get_maintenance_cost_breakdown(period: str = "last_6_months") -> dict`: Thống kê phân loại chi phí sửa chữa theo danh mục (điện, nước, điện lạnh, đồ gỗ).
- **Resources:**
  - `apartment://rules`: Nội quy tòa nhà định dạng Markdown.
  - `apartment://bulletin-latest`: Toàn văn các thông báo bảng tin mới nhất.

#### FR-LANDLORD-06: Quản lý Nhân khẩu & Lưu trú Chi tiết (Occupancy Deep Management)
- **Mục tiêu:** Giúp chủ nhà nắm bắt chính xác ai đang ở trong từng phòng, số lượng người thuê thực tế và quản lý hồ sơ đăng ký tạm trú công an.
- **Tác nhân:** Chủ căn hộ (`landlord`), Quản trị viên (`admin`).
- **Nghiệp vụ:**
  - Xem danh sách tổng quan toàn tòa nhà: Phòng nào đang có người ở (`occupied`), phòng nào trống (`vacant`).
  - Đi sâu vào từng phòng (Drill-down):
    - Khách thuê đại diện hợp đồng (Họ tên, SĐT, Email, CCCD, ngày ký, hạn hợp đồng).
    - Số lượng người ở thực tế trong phòng (Ví dụ: Phòng 302 có 3 người đang cư trú).
    - Chi tiết từng thành viên ở cùng (`roommates`): Họ tên, số điện thoại, số CCCD, ngày sinh, quê quán, biển số xe máy để cấp thẻ gửi xe, tình trạng duyệt tạm trú.
  - Cập nhật trạng thái tạm trú công an (`pending` $\rightarrow$ `registered`) sau khi chủ nhà đã nộp hồ sơ lên cổng dịch vụ công quản lý cư trú.
  - Xuất file danh sách cư dân (CSV/Excel) để nộp công an khu vực khi có đợt kiểm tra hành chính.

#### FR-LANDLORD-07: Tạo Hóa đơn Nhanh & Chụp ảnh Công tơ Trực tiếp (Quick Invoicing & Photo Proof)
- **Mục tiêu:** Hỗ trợ chủ nhà hoặc nhân viên quản lý đi chốt số điện nước tại hiện trường, chụp ảnh lưu bằng chứng và xuất hóa đơn ngay lập tức trong 30 giây.
- **Tác nhân:** Chủ căn hộ (`landlord`), Quản trị viên (`admin`).
- **Luồng xử lý:**
  1. Chủ nhà cầm điện thoại mở tính năng "Tạo hóa đơn nhanh" trên giao diện web.
  2. Chọn số phòng (VD: Phòng 204).
  3. Mở camera chụp ảnh trực tiếp đồng hồ điện và đồng hồ nước tại cửa phòng.
  4. Hệ thống tự động upload ảnh, gọi **Gemini Vision OCR** trích xuất chỉ số mới, đồng thời lưu trữ file ảnh vào `/uploads/meters/` làm bằng chứng pháp lý đối chiếu nếu khách thắc mắc.
  5. Hiển thị bảng tính nháp: Chỉ số cũ $\rightarrow$ Chỉ số mới $\rightarrow$ Số kWh/m3 tiêu thụ $\rightarrow$ Thành tiền.
  6. Chủ nhà kiểm tra số, có thể chỉnh sửa tay nếu ảnh mờ, bấm "Phát hành hóa đơn ngay".
  7. Hóa đơn được tạo với mã VietQR chuẩn xác và thông báo gửi tức thì đến tài khoản của khách thuê phòng đó.

#### FR-LANDLORD-08: Hệ thống Cảnh báo Vi phạm Nội quy & Phạt Tiền Lũy tiến (Violation Warning & Progressive Penalty)
- **Mục tiêu:** Giữ gìn an ninh trật tự, nếp sống văn minh và an toàn phòng cháy chữa cháy (PCCC) trong khu căn hộ cho thuê.
- **Tác nhân:** Chủ căn hộ (`landlord`), Quản trị viên (`admin`), Khách thuê phản ánh (`tenant`).
- **5 Nhóm vi phạm thực tế trong quản lý căn hộ:**
  1. **Tiếng ồn sau 22h (`noise`):** Mở nhạc lớn, hát karaoke, tiệc tùng gây mất trật tự sau khung giờ yên tĩnh quy định (22:00 - 06:00).
  2. **Vệ sinh & Rác thải (`hygiene`):** Để rác bừa bãi trước cửa phòng hoặc hành lang chung, không phân loại rác, để giày dép cản trở lối đi chung, nuôi thú cưng để phóng uế bừa bãi.
  3. **An toàn PCCC & Cửa an ninh (`fire_safety`):** Không khóa cổng an ninh khi ra vào ban đêm (sau 23:00), che chắn bình chữa cháy hoặc chèn cửa thoát hiểm, sạc xe máy điện qua đêm ở khu vực cấm hoặc câu móc dây điện nguy hiểm.
  4. **Quy định Khách thăm & Lưu trú (`guest_policy`):** Dẫn người lạ vào ở qua đêm không thông báo/khai báo tạm trú theo luật cư trú, cho mượn thẻ từ/chìa khóa tùy tiện.
  5. **Hút thuốc khu vực cấm (`smoking`):** Hút thuốc lá/thuốc lá điện tử trong thang máy, hành lang kín, hoặc trong phòng có đầu phun báo khói tự động gây kích hoạt chuông báo động giả.
- **Cơ chế xử lý 3 cấp độ lũy tiến (3-Tier Severity Level):**
  - **Mức 1 - Nhắc nhở (`reminder`):** Vi phạm lần 1 mang tính vô ý. Gửi thông báo nhắc nhở nhẹ nhàng trên app và SMS/Zalo. Tiền phạt: 0đ.
  - **Mức 2 - Cảnh cáo chính thức (`warning`):** Tái phạm lần 2 hoặc vi phạm nghiêm trọng (như quên khóa cổng đêm). Lập biên bản điện tử gửi khách thuê kèm ảnh chứng cứ (trích xuất camera hoặc ảnh phản ánh). Yêu cầu khách bấm xác nhận cam kết không tái phạm. Tiền phạt: 0đ - 100.000đ (phí vệ sinh/nhắc nhở).
  - **Mức 3 - Phạt tiền quy chế (`penalty`):** Tái phạm từ lần 3 trở lên hoặc vi phạm cố ý gây thiệt hại. Áp dụng mức phạt từ 200.000đ đến 1.000.000đ tùy theo quy chế tòa nhà đã thỏa thuận trong hợp đồng.
  - **Tích hợp tự động vào dòng tiền:** Khoản tiền phạt được tự động nạp vào hóa đơn tiền phòng tháng tiếp theo với mục `invoice_items` (`item_type='penalty'`), bảo đảm chủ nhà thu được đúng chế tài mà không cần đòi riêng.

---

### 4.3. Phân hệ Quản trị & Xác thực (Auth & RBAC Subsystem)

#### FR-AUTH-01: Xác thực JWT Stateless & Mã hóa Mật khẩu
- **Cơ chế:** Cấp phát Access Token (thời hạn 24 giờ) và Refresh Token (thời hạn 30 ngày) khi đăng nhập thành công.
- **Mã hóa:** Sử dụng thư viện `passlib` hoặc `argon2-cffi` / `bcrypt` để băm mật khẩu với salt ngẫu nhiên, độ an toàn cao chống tấn công từ điển.
- **Role-based Middleware:**
  - Decorator `@admin_required`: Chỉ cho phép role `admin`.
  - Decorator `@landlord_required`: Cho phép role `admin` hoặc `landlord`.
  - Decorator `@tenant_required`: Cho phép role `tenant`.

#### FR-AUTH-02: Đăng ký Tài khoản (User Registration) & Cấp quyền Tự động
- **Mục tiêu:** Cho phép khách thuê mới tự tạo tài khoản trên web để tra cứu thông tin phòng và gửi yêu cầu thuê.
- **Tác nhân:** Người dùng vãng lai (`public`).
- **Quy trình:**
  - Nhập Họ và tên, Email, Số điện thoại, Tên đăng nhập, Mật khẩu.
  - Sau khi đăng ký thành công, tài khoản mặc định có quyền `role = 'tenant'`.
  - Khi chủ nhà tạo hợp đồng thuê và gán `tenant_id` trùng khớp với tài khoản, tài khoản sẽ tự động liên kết với phòng và kích hoạt toàn bộ tính năng của khách thuê (xem phòng, khai báo người ở cùng, nhận hóa đơn, quét mã VietQR, chụp số điện nước).

---

## 5. ĐẶC TẢ CƠ SỞ DỮ LIỆU & LƯỢC ĐỒ (DATABASE SCHEMA SPECIFICATION)

Cơ sở dữ liệu sử dụng **SQLite 3** cấu hình chế độ **WAL (Write-Ahead Logging)**, gồm **12 bảng chuẩn hóa 3NF**:

```
+----------------------------------------------------------------------------------------------------+
|                                    DATABASE SCHEMA MAP (12 TABLES)                                 |
+----------------------+----------------------+----------------------+-------------------------------+
| CORE ENTITIES        | CONTRACTS & BILLING  | ASSETS & OPERATIONS  | RESIDENCE & DISCIPLINE        |
+----------------------+----------------------+----------------------+-------------------------------+
| • users              | • contracts          | • room_assets        | • roommates                   |
| • buildings          | • invoices           | • expenses           | • room_violations             |
| • rooms              | • invoice_items      | • utility_readings   | • service_tickets             |
|                      |                      |                      | • bulletin_announcements      |
|                      |                      |                      | • chat_sessions               |
+----------------------+----------------------+----------------------+-------------------------------+
```

### 5.1. Bảng `users` (Tài khoản người dùng)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Mã định danh duy nhất |
| `username` | VARCHAR(50) | UNIQUE, NOT NULL | Tên đăng nhập |
| `email` | VARCHAR(100) | UNIQUE, NOT NULL | Địa chỉ email liên hệ |
| `password_hash` | VARCHAR(255) | NOT NULL | Mật khẩu băm an toàn |
| `role` | VARCHAR(20) | NOT NULL, DEFAULT 'tenant' | Vai trò: `admin`, `landlord`, `tenant` |
| `full_name` | VARCHAR(100) | NOT NULL | Họ và tên đầy đủ |
| `phone` | VARCHAR(20) | NOT NULL | Số điện thoại |
| `cccd_number` | VARCHAR(20) | NULL | Số Căn cước công dân (khai báo tạm trú) |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Thời điểm tạo tài khoản |

### 5.2. Bảng `buildings` (Tòa nhà quản lý)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Mã định danh tòa nhà |
| `name` | VARCHAR(100) | NOT NULL | Tên tòa nhà (VD: SAMS Building 1) |
| `address` | VARCHAR(255) | NOT NULL | Địa chỉ chi tiết |
| `total_floors` | INTEGER | NOT NULL, DEFAULT 1 | Tổng số tầng |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Thời điểm tạo |

### 5.3. Bảng `rooms` (Danh mục căn hộ/phòng)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Mã phòng |
| `building_id` | INTEGER | NOT NULL, FK(`buildings.id`) | Thuộc tòa nhà nào |
| `current_tenant_id` | INTEGER | NULL, FK(`users.id`) | Khách thuê hiện tại (nếu có) |
| `room_number` | VARCHAR(20) | NOT NULL | Số phòng (VD: "302", "P.101") |
| `floor` | INTEGER | NOT NULL | Tầng |
| `base_price` | DECIMAL(12, 2) | NOT NULL | Giá thuê cơ bản hàng tháng (VNĐ) |
| `area_sqm` | DECIMAL(6, 2) | NOT NULL | Diện tích sử dụng (m2) |
| `status` | VARCHAR(20) | NOT NULL, DEFAULT 'vacant' | Trạng thái: `vacant`, `occupied`, `maintenance` |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Thời điểm tạo |

*Index:* `CREATE INDEX idx_rooms_building_status ON rooms(building_id, status);`

### 5.4. Bảng `room_assets` (Tài sản & Trang thiết bị trong phòng)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Mã tài sản |
| `room_id` | INTEGER | NOT NULL, FK(`rooms.id`) | Đặt tại phòng nào |
| `item_name` | VARCHAR(100) | NOT NULL | Tên đồ đạc (Điều hòa, Giường, Tủ lạnh...) |
| `brand_model` | VARCHAR(100) | NULL | Hãng & Model thiết bị |
| `serial_number` | VARCHAR(100) | NULL | Số serial máy móc |
| `condition` | VARCHAR(30) | NOT NULL, DEFAULT 'good' | Hiện trạng: `good`, `fair`, `damaged` |
| `image_url` | VARCHAR(255) | NULL | Đường dẫn ảnh hiện trạng lúc bàn giao |
| `verified_by_tenant` | BOOLEAN | NOT NULL, DEFAULT 0 | Khách thuê đã xác nhận lúc nhận phòng chưa |
| `verified_at` | DATETIME | NULL | Thời điểm khách bấm xác nhận |

### 5.5. Bảng `contracts` (Hợp đồng thuê căn hộ)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Mã hợp đồng |
| `room_id` | INTEGER | NOT NULL, FK(`rooms.id`) | Căn hộ thuê |
| `tenant_id` | INTEGER | NOT NULL, FK(`users.id`) | Khách thuê đại diện |
| `start_date` | DATE | NOT NULL | Ngày bắt đầu thuê |
| `end_date` | DATE | NOT NULL | Ngày kết thúc hợp đồng |
| `deposit_amount` | DECIMAL(12, 2) | NOT NULL | Số tiền đặt cọc giữ chỗ (VNĐ) |
| `monthly_rent` | DECIMAL(12, 2) | NOT NULL | Tiền thuê cố định mỗi tháng (VNĐ) |
| `status` | VARCHAR(20) | NOT NULL, DEFAULT 'active' | Trạng thái: `active`, `terminated`, `expired` |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Thời điểm lập hợp đồng |

*Index:* `CREATE INDEX idx_contracts_tenant_status ON contracts(tenant_id, status);`

### 5.6. Bảng `utility_readings` (Bản ghi chỉ số điện nước & ảnh OCR)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Mã bản ghi chốt số |
| `room_id` | INTEGER | NOT NULL, FK(`rooms.id`) | Phòng đo đạc |
| `meter_type` | VARCHAR(20) | NOT NULL | Loại công tơ: `electricity` hoặc `water` |
| `reading_value` | DECIMAL(10, 2) | NOT NULL | Chỉ số mới chốt được (kWh hoặc m3) |
| `previous_value` | DECIMAL(10, 2) | NOT NULL | Chỉ số tháng trước liền kề |
| `consumption` | DECIMAL(10, 2) | NOT NULL | Sản lượng tiêu thụ = `reading_value - previous_value` |
| `image_proof_url` | VARCHAR(255) | NOT NULL | Đường link ảnh chụp công tơ gốc |
| `ai_confidence` | FLOAT | NULL | Điểm tin cậy từ Gemini Vision (0.0 đến 1.0) |
| `month` | INTEGER | NOT NULL | Tháng ghi nhận (1 - 12) |
| `year` | INTEGER | NOT NULL | Năm ghi nhận |
| `recorded_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Thời điểm ghi nhận |

*Index:* `CREATE INDEX idx_utility_room_period ON utility_readings(room_id, month, year);`

### 5.7. Bảng `invoices` (Hóa đơn thu tiền hàng tháng)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Mã hóa đơn |
| `room_id` | INTEGER | NOT NULL, FK(`rooms.id`) | Căn hộ phát sinh hóa đơn |
| `contract_id` | INTEGER | NOT NULL, FK(`contracts.id`) | Hợp đồng tham chiếu |
| `month` | INTEGER | NOT NULL | Hóa đơn tháng nào |
| `year` | INTEGER | NOT NULL | Năm phát hành |
| `total_amount` | DECIMAL(12, 2) | NOT NULL | Tổng số tiền phải thanh toán (VNĐ) |
| `status` | VARCHAR(20) | NOT NULL, DEFAULT 'unpaid' | Trạng thái: `unpaid`, `paid`, `overdue` |
| `vietqr_payload` | TEXT | NULL | Chuỗi mã VietQR Napas EMVCo |
| `payment_ref` | VARCHAR(50) | NULL | Mã tham chiếu thanh toán (VD: `SAMS P302 T10`) |
| `due_date` | DATE | NOT NULL | Hạn chót thanh toán |
| `paid_at` | DATETIME | NULL | Thời điểm thanh toán thực tế |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Thời điểm xuất hóa đơn |

### 5.8. Bảng `invoice_items` (Chi tiết các mục trong hóa đơn)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Mã chi tiết |
| `invoice_id` | INTEGER | NOT NULL, FK(`invoices.id`) | Thuộc hóa đơn nào |
| `item_type` | VARCHAR(30) | NOT NULL | Loại mục: `rent`, `electricity`, `water`, `service`, `penalty` |
| `description` | VARCHAR(255) | NOT NULL | Diễn giải chi tiết (VD: Tiền điện: 85 kWh x 3.500đ) |
| `unit_price` | DECIMAL(12, 2) | NOT NULL | Đơn giá |
| `quantity` | DECIMAL(8, 2) | NOT NULL | Số lượng (kWh, m3, tháng) |
| `subtotal` | DECIMAL(12, 2) | NOT NULL | Thành tiền |

### 5.9. Bảng `expenses` (Chi phí vận hành tòa nhà OpEx)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Mã khoản chi |
| `building_id` | INTEGER | NOT NULL, FK(`buildings.id`) | Tòa nhà phát sinh chi phí |
| `recorded_by` | INTEGER | NOT NULL, FK(`users.id`) | Người lập phiếu chi |
| `expense_category` | VARCHAR(50) | NOT NULL | Phân loại chi: `common_electricity`, `water`, `internet`, `cleaning`, `security`, `maintenance` |
| `title` | VARCHAR(150) | NOT NULL | Tên khoản chi (VD: Tiền điện hành lang T10) |
| `amount` | DECIMAL(12, 2) | NOT NULL | Số tiền chi (VNĐ) |
| `receipt_image_url` | VARCHAR(255) | NULL | Ảnh chụp hóa đơn/biên lai chi tiền |
| `expense_date` | DATE | NOT NULL | Ngày chi thực tế |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Thời điểm lưu bản ghi |

*Index:* `CREATE INDEX idx_expenses_date_category ON expenses(expense_date, expense_category);`

### 5.10. Bảng `bulletin_announcements` (Bảng tin thông báo của tòa nhà)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Mã thông báo |
| `building_id` | INTEGER | NOT NULL, FK(`buildings.id`) | Thuộc tòa nhà nào |
| `author_id` | INTEGER | NOT NULL, FK(`users.id`) | Người đăng thông báo |
| `title` | VARCHAR(200) | NOT NULL | Tiêu đề thông báo |
| `content` | TEXT | NOT NULL | Nội dung chi tiết |
| `priority` | VARCHAR(20) | NOT NULL, DEFAULT 'normal' | Mức độ ưu tiên: `normal`, `important`, `emergency` |
| `effective_date` | DATE | NOT NULL | Ngày áp dụng |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Thời điểm đăng tải |

### 5.11. Bảng `service_tickets` (Yêu cầu sửa chữa & Hỗ trợ kỹ thuật)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Mã ticket |
| `room_id` | INTEGER | NOT NULL, FK(`rooms.id`) | Phòng xảy ra sự cố |
| `tenant_id` | INTEGER | NOT NULL, FK(`users.id`) | Khách thuê báo |
| `category` | VARCHAR(50) | NOT NULL | Danh mục: `repair`, `cleaning`, `security`, `other` |
| `title` | VARCHAR(150) | NOT NULL | Tóm tắt sự cố |
| `description` | TEXT | NOT NULL | Mô tả chi tiết hiện tượng |
| `image_url` | VARCHAR(255) | NULL | Ảnh chụp hiện trường hỏng hóc |
| `priority` | VARCHAR(20) | NOT NULL, DEFAULT 'medium' | Độ khẩn cấp: `low`, `medium`, `high`, `urgent` |
| `status` | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | Trạng thái: `pending`, `in_progress`, `resolved`, `cancelled` |
| `repair_cost` | DECIMAL(12, 2) | NOT NULL, DEFAULT 0 | Chi phí thực tế sửa chữa (nếu có) |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Thời điểm gửi yêu cầu |

### 5.12. Bảng `roommates` (Danh sách thành viên ở cùng & Quản lý tạm trú)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Mã định danh người ở |
| `room_id` | INTEGER | NOT NULL, FK(`rooms.id`) | Đang cư trú tại phòng nào |
| `contract_id` | INTEGER | NOT NULL, FK(`contracts.id`) | Gắn liền với hợp đồng thuê nào |
| `full_name` | VARCHAR(100) | NOT NULL | Họ và tên người ở cùng |
| `phone` | VARCHAR(20) | NOT NULL | Số điện thoại liên hệ |
| `cccd_number` | VARCHAR(20) | NOT NULL | Số CCCD/Định danh (bắt buộc khai báo tạm trú) |
| `date_of_birth` | DATE | NULL | Ngày tháng năm sinh |
| `gender` | VARCHAR(10) | NOT NULL, DEFAULT 'other' | Giới tính: `male`, `female`, `other` |
| `hometown` | VARCHAR(150) | NULL | Quê quán / Thường trú theo CCCD |
| `temporary_residence_status` | VARCHAR(30) | NOT NULL, DEFAULT 'pending' | Tình trạng tạm trú: `pending`, `registered`, `rejected` |
| `vehicle_plate` | VARCHAR(20) | NULL | Biển số xe máy (để cấp thẻ xe và quản lý an ninh bãi xe) |
| `is_primary_tenant` | BOOLEAN | NOT NULL, DEFAULT 0 | Có phải người đứng tên ký hợp đồng chính không |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Thời điểm thêm vào phòng |

*Index:* `CREATE INDEX idx_roommates_room_contract ON roommates(room_id, contract_id);`

### 5.13. Bảng `room_violations` (Biên bản vi phạm nội quy & Chế tài xử phạt)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Mã biên bản vi phạm |
| `room_id` | INTEGER | NOT NULL, FK(`rooms.id`) | Phòng vi phạm |
| `reported_by` | INTEGER | NOT NULL, FK(`users.id`) | Người phát hiện/lập biên bản (Chủ nhà hoặc Quản lý) |
| `violation_type` | VARCHAR(50) | NOT NULL | Nhóm: `noise`, `hygiene`, `fire_safety`, `guest_policy`, `smoking`, `other` |
| `severity` | VARCHAR(20) | NOT NULL, DEFAULT 'reminder' | Cấp độ: `reminder` (nhắc nhở), `warning` (cảnh cáo), `penalty` (phạt tiền) |
| `title` | VARCHAR(150) | NOT NULL | Tiêu đề vi phạm (VD: Hát karaoke sau 23h đêm) |
| `description` | TEXT | NOT NULL | Mô tả chi tiết hành vi và thời điểm xảy ra |
| `evidence_image_url` | VARCHAR(255) | NULL | Đường dẫn ảnh chụp/camera bằng chứng vi phạm |
| `penalty_amount` | DECIMAL(12, 2) | NOT NULL, DEFAULT 0 | Số tiền phạt (VNĐ) |
| `status` | VARCHAR(30) | NOT NULL, DEFAULT 'pending' | Trạng thái: `pending`, `acknowledged`, `penalized`, `resolved` |
| `invoice_item_id` | INTEGER | NULL, FK(`invoice_items.id`) | Liên kết tới mục tiền phạt trong hóa đơn thu tiền |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Thời điểm lập biên bản |
| `resolved_at` | DATETIME | NULL | Thời điểm giải quyết hoặc nộp phạt xong |

*Index:* `CREATE INDEX idx_violations_room_status ON room_violations(room_id, status);`

---

## 6. ĐẶC TẢ GIAO DIỆN API & GIAO THỨC (API & PROTOCOL SPECIFICATIONS)

### 6.1. RESTful API Endpoints Specification

Tất cả các REST API đều tuân thủ chuẩn **JSON:API Envelope**:
```json
{
  "success": true,
  "data": { ... },
  "meta": { "timestamp": "2026-10-01T12:00:00Z" },
  "error": null
}
```

#### Bảng tổng hợp Endpoints chính:

| Phương thức | Endpoint | Phân quyền | Chức năng nghiệp vụ |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Public | Đăng ký tài khoản người dùng mới (Role: `tenant`) |
| `POST` | `/api/v1/auth/login` | Public | Đăng nhập nhận JWT Access & Refresh Token |
| `GET` | `/api/v1/auth/me` | Authenticated | Lấy thông tin hồ sơ người dùng đang đăng nhập |
| `GET` | `/api/v1/rooms` | Landlord/Admin | Lấy danh sách toàn bộ phòng và trạng thái |
| `GET` | `/api/v1/rooms/search` | Public/Tenant | Tìm kiếm phòng trống theo khoảng giá, diện tích, tiện ích |
| `GET` | `/api/v1/rooms/my-room` | Tenant | Lấy thông tin phòng của khách thuê hiện tại |
| `GET` | `/api/v1/rooms/<id>/roommates` | Landlord/Tenant | Xem danh sách người ở cùng trong phòng |
| `POST` | `/api/v1/rooms/<id>/roommates` | Landlord/Tenant | Khai báo thêm người ở cùng (CCCD, SĐT, biển số xe) |
| `PUT` | `/api/v1/rooms/<id>/roommates/<rid>/status` | Landlord | Cập nhật trạng thái duyệt đăng ký tạm trú công an |
| `POST` | `/api/v1/meters/scan-reading` | Tenant | Tải ảnh công tơ điện nước lên để Gemini Vision OCR |
| `POST` | `/api/v1/meters/confirm-reading`| Tenant | Khách xác nhận lưu chỉ số công tơ vào CSDL |
| `POST` | `/api/v1/quick-invoices` | Landlord/Admin | Tạo hóa đơn nhanh tại chỗ từ ảnh công tơ điện nước |
| `GET` | `/api/v1/billing/my-invoices` | Tenant | Lấy danh sách hóa đơn của khách thuê (kèm link VietQR) |
| `POST` | `/api/v1/billing/<id>/payment-slip` | Tenant | Tải ảnh biên lai chuyển khoản ngân hàng |
| `POST` | `/api/v1/billing/generate` | Landlord/Admin | Tự động tính toán và phát hành hóa đơn cả tòa nhà |
| `GET` | `/api/v1/violations` | Landlord/Admin | Danh sách biên bản vi phạm nội quy tòa nhà |
| `POST` | `/api/v1/violations` | Landlord/Admin | Lập biên bản cảnh cáo / phạt vi phạm phòng |
| `PUT` | `/api/v1/violations/<id>/acknowledge` | Tenant | Khách xác nhận cam kết sau khi nhận cảnh cáo |
| `POST` | `/api/v1/assets/verify` | Tenant | Khách xác nhận checklist tài sản khi nhận phòng |
| `POST` | `/api/v1/expenses` | Landlord/Admin | Ghi nhận chi phí vận hành OpEx mới |
| `GET` | `/api/v1/expenses/net-profit` | Landlord/Admin | Lấy số liệu Doanh thu vs OpEx vs Lợi nhuận ròng |
| `POST` | `/api/v1/contracts/refund` | Landlord/Admin | Tính quyết toán trừ cọc hoàn tiền khi trả phòng |
| `POST` | `/api/v1/chat/message` | Tenant | Gửi tin nhắn đàm thoại với Trợ lý ảo Gemini |
| `GET` | `/api/v1/announcements` | Tenant/Landlord | Xem danh sách thông báo bảng tin tòa nhà |

---

### 6.2. Model Context Protocol (MCP) Server Specification

MCP Server chạy trên tiến trình độc lập (`port 8000`), lắng nghe giao thức Server-Sent Events (SSE) tại `/sse` và HTTP POST tại `/messages`.

#### Định nghĩa Cấu trúc Schema 9 Tools cho LLM Host:

```python
# mcp_server/tools/financial_tools.py
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

mcp = FastMCP("SAMS-Apartment-Intelligence")

class MonthlyRevenueInput(BaseModel):
    month: int = Field(..., description="Tháng cần tra cứu (1-12)", ge=1, le=12)
    year: int = Field(..., description="Năm cần tra cứu (VD: 2026)", ge=2020)

@mcp.tool(name="get_monthly_revenue", description="Thống kê tổng doanh thu hóa đơn căn hộ trong tháng, bao gồm số tiền đã thanh toán, chưa thanh toán và nợ đọng.")
def get_monthly_revenue(params: MonthlyRevenueInput) -> dict:
    ...

class NetProfitInput(BaseModel):
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2020)

@mcp.tool(name="get_net_profit_summary", description="Báo cáo Lợi nhuận Ròng: Tính toán tổng thực thu từ khách trừ đi toàn bộ chi phí vận hành OpEx (điện chung, nước, rác, sửa chữa) trong tháng.")
def get_net_profit_summary(params: NetProfitInput) -> dict:
    ...

class DebtorListInput(BaseModel):
    grace_period_days: int = Field(default=5, description="Số ngày quá hạn cho phép trước khi liệt kê vào danh sách nợ đọng")

@mcp.tool(name="get_debtor_list", description="Lấy danh sách các phòng quá hạn thanh toán tiền phòng kèm số điện thoại liên hệ và số tiền nợ.")
def get_debtor_list(params: DebtorListInput) -> list:
    ...

class OccupancyReportInput(BaseModel):
    building_id: int = Field(..., description="Mã tòa nhà cần thống kê nhân khẩu và lưu trú")

@mcp.tool(name="get_occupancy_report", description="Báo cáo tỷ lệ lấp đầy: Ai đang thuê phòng nào, phòng có bao nhiêu người ở, danh sách CCCD người ở cùng và tình trạng đăng ký tạm trú công an.")
def get_occupancy_report(params: OccupancyReportInput) -> dict:
    ...

class RoomViolationsSummaryInput(BaseModel):
    room_id: int = Field(..., description="Mã phòng cần tra cứu lịch sử vi phạm")

@mcp.tool(name="get_room_violations_summary", description="Tra cứu lịch sử vi phạm nội quy của phòng: Tiếng ồn, rác thải, PCCC, hút thuốc, số lần nhắc nhở, cảnh cáo và tổng tiền phạt đã áp dụng.")
def get_room_violations_summary(params: RoomViolationsSummaryInput) -> list:
    ...

class ExpirationForecastInput(BaseModel):
    days: int = Field(default=45, description="Khoảng thời gian dự báo sắp hết hạn (tính bằng ngày)")

@mcp.tool(name="get_contract_expiration_forecast", description="Dự báo các phòng sẽ hết hạn hợp đồng trong N ngày tới để chủ nhà chủ động tìm khách mới tránh trống phòng.")
def get_contract_expiration_forecast(params: ExpirationForecastInput) -> list:
    ...
```

---

### 6.3. Gemini API Integration Specification (LLM & Vision)

#### A. Pipeline Gemini Vision OCR Đọc Công tơ Điện Nước
1. **Model:** `gemini-1.5-flash`
2. **System Instruction:**
   ```text
   Bạn là một hệ thống AI OCR chuyên dụng phân tích công tơ điện nước dân dụng Việt Nam.
   Nhiệm vụ: Trích xuất chính xác con số chỉ số đang hiển thị trên mặt số đồng hồ.
   Đối với công tơ điện cơ học: Chỉ lấy phần số nguyên màu đen, bỏ qua chữ số màu đỏ sau dấu phẩy nếu có.
   Chỉ xuất ra kết quả định dạng JSON nghiêm ngặt, không thêm giải thích:
   {
     "reading": <float>,
     "confidence": <float 0.0 - 1.0>,
     "detected_type": "electricity" | "water",
     "notes": "<ghi chú nếu ảnh mờ hoặc lóa>"
   }
   ```

#### B. Pipeline Gemini Assistant Đàm thoại & Function Calling
1. **Model:** `gemini-1.5-flash`
2. **System Instruction:**
   ```text
   Bạn là Trợ lý Ảo Thông Minh của Tòa nhà Căn hộ SAMS. Bạn đang hỗ trợ khách thuê có tên là: {tenant_name}, đang ở phòng: {room_number}.
   Quy tắc ứng xử:
   1. Luôn lịch sự, thân thiện, trả lời bằng tiếng Việt chuẩn mực.
   2. Khi khách hỏi về tiền phòng, tiền điện nước, hoặc hợp đồng: BẮT BUỘC gọi Function Call tương ứng để lấy dữ liệu thực tế từ hệ thống, KHÔNG ĐƯỢC TỰ ĐOÁN SỐ TIỀN.
   3. Khi khách báo hỏng đồ đạc: Hỏi rõ vị trí, biểu hiện và tự động gọi hàm tạo ticket hỗ trợ.
   4. Cung cấp thông tin nội quy tòa nhà chính xác dựa trên bảng nội quy được cung cấp.
   ```
3. **Danh sách Function Call Declarations:**
   - `get_unpaid_invoices()`
   - `get_contract_details()`
   - `create_maintenance_ticket(category, description, priority)`
   - `get_building_announcements()`

---

## 7. YÊU CẦU PHI CHỨC NĂNG (NON-FUNCTIONAL REQUIREMENTS - NFRs)

### 7.1. Hiệu năng & Khả năng xử lý đồng thời (Performance & Concurrency)
- **SQLite Concurrency Throughput:** Nhờ chế độ **WAL Mode**, hệ thống phải hỗ trợ tối thiểu **50 requests đọc đồng thời** từ MCP Server và Web UI trong khi **1 tiến trình ghi** của Flask đang cập nhật mà không gây ra hiện tượng `database is locked`.
- **Thời gian phản hồi API (Latency):**
  - Các API CRUD thông thường: Thời gian phản hồi $t_{response} < 100ms$.
  - API xử lý ảnh Gemini Vision OCR: $t_{response} < 2.0s$.
  - API Chat Gemini Streaming: Bắt đầu trả token đầu tiên (Time to First Token) $t_{TTFT} < 800ms$.
- **Tối ưu tài nguyên container:** Tổng mức sử dụng RAM của cả hệ thống (4 containers) trên Docker không vượt quá **500MB RAM**, đảm bảo vận hành ổn định trên các gói VPS giá rẻ (1 vCPU, 1GB RAM).

### 7.2. Bảo mật & An toàn Dữ liệu (Security)
- **Bảo mật truy cập chéo phòng (Tenant Isolation):** Mọi truy vấn của khách thuê đều được backend tự động chèn mệnh đề `WHERE room_id = current_user.room_id`. Tuyệt đối không cho phép khách thuê truyền `room_id` tùy ý trên URL/Body để xem trộm phòng khác.
- **Bảo vệ Prompt Injection:** Làm sạch (sanitize) mọi chuỗi input của người dùng trước khi ghép vào prompt gửi cho Gemini API.
- **Bảo mật file ảnh tải lên:** Chỉ cho phép các định dạng ảnh (`.jpg`, `.jpeg`, `.png`, `.webp`), đổi tên file ảnh thành chuỗi UUID ngẫu nhiên trước khi lưu trên đĩa cứng để ngăn ngừa lỗ hổng Path Traversal.

### 7.3. Tính khả dụng & Khả năng phục hồi (Reliability & Recovery)
- **Docker Healthchecks:** Thiết lập lệnh healthcheck tự động định kỳ 30 giây cho cả backend và frontend.
- **SQLite Auto-checkpoint:** Cấu hình SQLite tự động dọn dẹp file nhật ký WAL khi dung lượng đạt 1000 trang (`PRAGMA wal_autocheckpoint = 1000;`).
- **Sao lưu Database 1-chạm:** Cung cấp script sao lưu tự động file `apartment.db` ra thư mục `backups/` an toàn theo lịch trình hàng ngày.

---

## 8. MA TRẬN TRUY VẾT & QUY TẮC MÃ HÓA CHO AI (AI CODING GUIDELINES)

Để đảm bảo các AI Coding Assistant và kỹ sư phát triển triển khai mã nguồn chuẩn chỉ 100%, các quy tắc sau đây là **bắt buộc tuân thủ (MANDATORY)**:

### 8.1. Quy tắc lập trình Backend (Flask & Python Pro)
1. **Kiến trúc phân tầng rành mạch:**
   - `api/`: Chỉ nhận request, validate bằng Pydantic, gọi Service và trả về JSON Envelope. Không viết câu lệnh SQL hay nghiệp vụ phức tạp trong controller.
   - `services/`: Chứa 100% logic nghiệp vụ (tính tiền, gọi Gemini, sinh VietQR, kiểm tra điều kiện hoàn cọc).
   - `repositories/`: Chứa các thao tác đọc/ghi CSDL qua SQLAlchemy ORM hoặc raw parameterized queries.
2. **Quản lý kết nối Database:**
   - Luôn sử dụng context manager hoặc session scoped:
     ```python
     with get_db() as db:
         # Thao tác đọc/ghi
     ```
   - Giải phóng kết nối ngay lập tức trước khi gọi các dịch vụ mạng kéo dài (như Gemini API) để tránh giữ khóa ghi của SQLite.

### 8.2. Quy tắc lập trình Frontend (React 18 & UI/UX)
1. **Xử lý Chatbot Streaming:** Sử dụng `fetch` với `ReadableStream` hoặc thư viện `@microsoft/fetch-event-source` để đọc từng mẩu tin nhắn trả về từ Flask SSE endpoint.
2. **VietQR Display:** Hiển thị mã QR rõ ràng ở vị trí trung tâm, cung cấp thông tin số tiền và ngân hàng bằng chữ đậm bên dưới để khách đối chiếu.
3. **Responsive Mobile-First:** Mọi nút bấm chụp ảnh, quét mã, gửi tin nhắn chat phải có kích thước tối thiểu $44 \times 44$ pixel để thao tác dễ dàng bằng một ngón tay cái trên điện thoại.

### 8.3. Ma trận Bàn giao Trách nhiệm (Responsibility Matrix)
- **Phùng Thiên Trường:**
  - `backend/app/models/*` (10 models chuẩn hóa)
  - `backend/app/services/billing_service.py` & `vietqr_service.py`
  - `backend/app/services/gemini_vision_service.py` & `gemini_chat_service.py`
  - `backend/app/services/expense_service.py` & `refund_service.py`
  - `mcp_server/*` (FastMCP 7 tools & 2 resources)
- **Đinh Hoàng An:**
  - `frontend/src/components/chat/*` (Streaming Chat UI & Rich Cards)
  - `frontend/src/components/meters/*` (Camera OCR scanner & Confirmation)
  - `frontend/src/pages/tenant/*` (Bills, Move-in Checklist, Bulletin)
  - `frontend/src/pages/landlord/*` (Net Profit Dashboard, Refund Form, Rooms)
  - `docker-compose.yml`, `nginx/nginx.conf`, Dockerfiles & E2E Testing.

---

## 9. BỘ QUY TẮC THIẾT KẾ CHỐNG "AI SLOP" & TIÊU CHUẨN TAILWIND DESIGN SYSTEM

Tài liệu quy tắc riêng biệt tham chiếu tại: [anti_ai_slop_design_rules.md](.agents/rules/anti_ai_slop_design_rules.md).  
Nhằm đảm bảo giao diện đạt đẳng cấp thương mại cao, mọi AI và lập trình viên phải tuân thủ nghiêm ngặt 7 điều răn sau:

1. **CẤM GRADIENT TÍM/HỒNG NEON VÔ NGHĨA:**
   - Cấm các dải màu gradient cliché (`from-purple-500 to-pink-500`).
   - Bắt buộc dùng bảng màu **Slate & Deep Indigo** chuẩn mực tài chính & bất động sản.
   - 100% sử dụng **Semantic Design Tokens** (`bg-background`, `text-foreground`, `bg-card`, `border-border`, `bg-primary`, `bg-muted`). Mọi component phải tự động hỗ trợ Dark/Light mode không tì vết.
2. **CẤM BO GÓC BỪA BÃI & CARD LỘN XỘN:**
   - Cấm `rounded-3xl` hay `rounded-full` trên các card nội dung lớn.
   - Thẻ Card/Modal: `rounded-lg` (8px) hoặc `rounded-xl` (12px).
   - Nút bấm/Input: `rounded-md` (6px).
   - Cấm đổ bóng đen kịt dày đặc (`shadow-2xl`). Bắt buộc dùng viền tinh tế kết hợp bóng nhẹ: `border border-border/60 shadow-sm`.
3. **BẮT BUỘC ĐỦ 5 TRẠNG THÁI GIAO DIỆN (5 MANDATORY STATES):**
   - **Loading:** Bắt buộc dùng **Skeleton Loader** (`animate-pulse bg-muted`). Cấm để màn hình trắng hay giật cục.
   - **Empty:** Khi không có dữ liệu, bắt buộc có Icon Lucide trực quan, thông điệp rõ ràng và Nút kêu gọi hành động (CTA).
   - **Error:** Hộp thông báo lỗi viền đỏ dịu (`border-destructive/30 bg-destructive/10 text-destructive`), có nút "Thử lại".
   - **Submitting:** Nút bấm bắt buộc có spinner quay tròn `<Loader2 className="animate-spin" />` và `disabled={isSubmitting}`.
   - **Success:** Cấm `alert()` trình duyệt. Bắt buộc dùng **Toast Notification** tự ẩn sau 3 giây.
4. **BẮT BUỘC MOBILE-FIRST & CHUẨN TOUCH TARGETS:**
   - Nút bấm và vùng chạm tối thiểu **44px** (`h-11` hoặc `min-h-[44px]`).
   - Cấm thanh cuộn ngang vỡ layout trên mobile.
   - Bảng dữ liệu phức tạp tự động chuyển thành Card View xếp dọc trên màn hình nhỏ `< 640px`.
5. **CẤM MINH HỌA HOẠT HÌNH 3D TRẺ CON & SỐ LIỆU GIẢ VÔ LÝ:**
   - Thống nhất duy nhất 1 bộ icon vector: **Lucide React** (`strokeWidth={1.75}`).
   - Dữ liệu tiền tệ luôn định dạng có dấu chấm phân cách hàng nghìn (`3.500.000 đ`).
6. **CHUẨN MỰC TAILWIND CVA & ACCESSIBILITY:**
   - Cấm arbitrary values tùy tiện (`w-[347px]`, `mt-[23px]`). Tuân thủ Spacing Scale chuẩn của Tailwind.
   - Đóng gói component qua **Class Variance Authority (CVA)** và hàm `cn()`.
   - Mọi phần tử tương tác phải có Focus Ring: `focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2`.
7. **TRẢI NGHIỆM AI STREAMING ĐẲNG CẤP:**
   - Bắt buộc có Typing Indicator (ba chấm nhảy `animate-bounce`) khi AI đang xử lý.
   - Hỗ trợ Streaming Markdown Rendering theo thời gian thực.
   - Kết quả tra cứu hóa đơn phải render thẻ **Rich Card** có nút "Xem VietQR" trực tiếp trong dòng tin nhắn của bot, không chỉ in ra text thô.

---
**Tài liệu SRS này đã hoàn tất thẩm định, tích hợp bộ quy tắc Anti-AI Slop và là căn cứ kỹ thuật chính thức duy nhất để bắt đầu khởi tạo dự án.**
