"""
SAMS - Sprint 2 Automated Tests
Kiểm thử toàn diện: VietQR, OCR chốt số điện nước, Hóa đơn nhanh, Phạt vi phạm 3 cấp, và AI Chatbot.
"""
import io
from decimal import Decimal
from app.services.vietqr_service import VietQRService
from app.services.violation_service import ViolationService
from app.services.billing_service import BillingService


def test_vietqr_emvco_payload_and_crc():
    """Kiểm tra giải thuật sinh mã VietQR Napas247 chuẩn EMVCo và CRC-16."""
    payload = VietQRService.generate_emvco_payload(
        bank_bin="970422",
        account_number="0987654321",
        amount=5147500,
        message="SAMS P302 T10",
    )
    assert payload.startswith("000201010212")
    assert "970422" in payload
    assert "0987654321" in payload
    assert "5147500" in payload
    assert "SAMS P302 T10" in payload
    assert payload[-4:].isalnum()

    # Image URL
    url = VietQRService.generate_vietqr_image_url(
        bank_bin="970422",
        account_number="0987654321",
        amount=5147500,
        message="SAMS P302 T10",
    )
    assert "img.vietqr.io/image/970422-0987654321-compact2.png" in url
    assert "amount=5147500" in url


def test_meter_reading_scan_and_confirm(client, tenant_token, seed_data):
    """Kiểm tra API upload ảnh công tơ điện nước và xác nhận chỉ số."""
    room = seed_data["room"]
    headers = {"Authorization": f"Bearer {tenant_token}"}

    # Giả lập file ảnh 1x1 png
    dummy_img = io.BytesIO(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )

    # 1. Quét ảnh
    scan_res = client.post(
        "/api/v1/meters/scan-reading",
        headers=headers,
        data={
            "room_id": str(room.id),
            "meter_type": "electricity",
            "image": (dummy_img, "test_meter.png"),
        },
        content_type="multipart/form-data",
    )
    assert scan_res.status_code == 200
    scan_json = scan_res.get_json()
    assert scan_json["success"] is True
    assert "detected_reading" in scan_json["data"]
    detected_val = scan_json["data"]["detected_reading"]

    # 2. Xác nhận chỉ số vào DB
    confirm_res = client.post(
        "/api/v1/meters/confirm-reading",
        headers=headers,
        json={
            "room_id": room.id,
            "meter_type": "electricity",
            "confirmed_reading": detected_val,
            "month": 10,
            "year": 2026,
        },
    )
    assert confirm_res.status_code == 201
    confirm_json = confirm_res.get_json()
    assert confirm_json["success"] is True
    assert confirm_json["data"]["reading_value"] == detected_val


def test_violation_lifecycle_and_penalty(client, landlord_token, tenant_token, seed_data):
    """Kiểm tra quy trình vi phạm: Nhắc nhở -> Cảnh cáo -> Phạt tiền và Tenant xác nhận."""
    room = seed_data["room"]
    landlord_headers = {"Authorization": f"Bearer {landlord_token}"}
    tenant_headers = {"Authorization": f"Bearer {tenant_token}"}

    # 1. Chủ nhà lập biên bản vi phạm phạt tiền tiếng ồn sau 22h
    res = client.post(
        "/api/v1/violations",
        headers=landlord_headers,
        json={
            "room_id": room.id,
            "violation_type": "noise",
            "severity": "penalty",
            "title": "Hát karaoke sau 23h đêm",
            "description": "Bị phản ánh bởi các phòng xung quanh",
            "penalty_amount": 200000,
        },
    )
    assert res.status_code == 201
    v_data = res.get_json()["data"]
    v_id = v_data["violation_id"]
    assert v_data["penalty_amount"] == 200000.0
    assert v_data["status"] == "pending"

    # 2. Khách thuê xem danh sách vi phạm của phòng mình
    list_res = client.get("/api/v1/violations", headers=tenant_headers)
    assert list_res.status_code == 200
    violations = list_res.get_json()["data"]
    assert len(violations) == 1
    assert violations[0]["id"] == v_id

    # 3. Khách thuê xác nhận đã đọc biên bản
    ack_res = client.put(f"/api/v1/violations/{v_id}/acknowledge", headers=tenant_headers)
    assert ack_res.status_code == 200
    assert ack_res.get_json()["data"]["status"] == "acknowledged"


def test_quick_invoice_with_meter_and_penalties(client, landlord_token, tenant_token, seed_data):
    """Kiểm tra tạo hóa đơn nhanh có tự động cộng tiền điện, nước, phòng, dịch vụ và khoản phạt."""
    room = seed_data["room"]
    landlord_headers = {"Authorization": f"Bearer {landlord_token}"}
    tenant_headers = {"Authorization": f"Bearer {tenant_token}"}

    # Tạo trước 1 khoản phạt vi phạm 200.000đ
    client.post(
        "/api/v1/violations",
        headers=landlord_headers,
        json={
            "room_id": room.id,
            "violation_type": "hygiene",
            "severity": "penalty",
            "title": "Vứt rác bừa bãi trước cửa phòng",
            "penalty_amount": 100000,
        },
    )

    dummy_img = io.BytesIO(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )

    # Lập hóa đơn nhanh Tháng 10/2026: Điện 100 kWh, Nước 10 m3
    invoice_res = client.post(
        "/api/v1/quick-invoices",
        headers=landlord_headers,
        data={
            "room_id": str(room.id),
            "month": "10",
            "year": "2026",
            "electricity_reading": "100",
            "water_reading": "10",
            "electricity_image": (dummy_img, "elec.png"),
        },
        content_type="multipart/form-data",
    )
    assert invoice_res.status_code == 201
    inv_data = invoice_res.get_json()["data"]
    invoice_id = inv_data["invoice_id"]
    assert inv_data["status"] == "unpaid"
    assert inv_data["vietqr_url"] is not None

    # Kiểm tra các mục hóa đơn:
    # Rent: 4,500,000
    # Elec: 100 * 3,500 = 350,000
    # Water: 10 * 25,000 = 250,000
    # Service: 100,000 + 50,000 = 150,000
    # Penalty: 100,000
    # Total = 4,500,000 + 350,000 + 250,000 + 150,000 + 100,000 = 5,350,000
    item_types = [it["item_type"] for it in inv_data["items"]]
    assert "rent" in item_types
    assert "electricity" in item_types
    assert "water" in item_types
    assert "service" in item_types
    assert "penalty" in item_types
    assert inv_data["total_amount"] == 5350000.0

    # 4. Khách thuê xem hóa đơn trong mục my-invoices
    my_inv_res = client.get("/api/v1/billing/my-invoices", headers=tenant_headers)
    assert my_inv_res.status_code == 200
    my_invoices = my_inv_res.get_json()["data"]
    assert len(my_invoices) >= 1
    target_inv = next(i for i in my_invoices if i["id"] == invoice_id)
    assert target_inv["status"] == "unpaid"

    # 5. Khách thuê upload biên lai chuyển khoản ngân hàng
    dummy_slip = io.BytesIO(b"fake-image-bytes-slip")
    slip_res = client.post(
        f"/api/v1/billing/{invoice_id}/payment-slip",
        headers=tenant_headers,
        data={"slip_image": (dummy_slip, "receipt.jpg")},
        content_type="multipart/form-data",
    )
    assert slip_res.status_code == 200
    assert slip_res.get_json()["data"]["status"] == "pending_verification"

    # 6. Chủ nhà xác nhận thanh toán
    confirm_res = client.post(
        f"/api/v1/billing/invoices/{invoice_id}/confirm-payment",
        headers=landlord_headers,
    )
    assert confirm_res.status_code == 200
    assert confirm_res.get_json()["data"]["status"] == "paid"


def test_ai_chat_assistant_flow(client, tenant_token, landlord_token, seed_data):
    """Kiểm tra đàm thoại AI: tra cứu tiền phòng trả về thẻ VietQR, tra cứu nội quy."""
    tenant_headers = {"Authorization": f"Bearer {tenant_token}"}
    landlord_headers = {"Authorization": f"Bearer {landlord_token}"}
    room = seed_data["room"]

    # Tạo 1 hóa đơn để AI tra cứu
    client.post(
        "/api/v1/quick-invoices",
        headers=landlord_headers,
        data={"room_id": str(room.id), "month": "10", "year": "2026", "electricity_reading": "50"},
    )

    # 1. Hỏi tiền phòng / hóa đơn
    res = client.post(
        "/api/v1/chat/message",
        headers=tenant_headers,
        json={"message": "Hóa đơn tháng này của tôi hết bao nhiêu tiền?"},
    )
    assert res.status_code == 200
    chat_data = res.get_json()["data"]
    assert "reply" in chat_data
    assert chat_data["function_called"] == "get_unpaid_invoices"
    assert chat_data["attached_action"] is not None
    assert chat_data["attached_action"]["type"] == "VIETQR_PAYMENT_CARD"
    assert "vietqr_url" in chat_data["attached_action"]

    # 2. Hỏi nội quy
    rules_res = client.post(
        "/api/v1/chat/message",
        headers=tenant_headers,
        json={"message": "Cho mình hỏi nội quy giờ giấc và khóa cổng của tòa nhà?"},
    )
    assert rules_res.status_code == 200
    rules_data = rules_res.get_json()["data"]
    assert rules_data["function_called"] == "get_building_rules"
    assert "khóa cổng" in rules_data["reply"].lower() or "quy định" in rules_data["reply"].lower()


def test_service_tickets_and_announcements_flow(client, tenant_token, landlord_token, seed_data):
    """Kiểm tra quy trình tạo ticket báo hỏng, đổi trạng thái và thông báo tòa nhà."""
    tenant_headers = {"Authorization": f"Bearer {tenant_token}"}
    landlord_headers = {"Authorization": f"Bearer {landlord_token}"}
    room = seed_data["room"]

    # 1. Khách thuê tạo ticket báo hỏng
    ticket_payload = {
        "room_id": room.id,
        "title": "Hỏng bóng đèn phòng tắm",
        "description": "Bóng đèn chớp tắt liên tục cần thay bóng mới",
        "priority": "medium",
        "category": "electrical"
    }
    create_res = client.post("/api/v1/tickets", headers=tenant_headers, json=ticket_payload)
    assert create_res.status_code == 201
    ticket_id = create_res.get_json()["data"]["id"]
    assert create_res.get_json()["data"]["status"] == "pending"

    # 2. Khách thuê xem danh sách ticket của mình
    list_res = client.get("/api/v1/tickets", headers=tenant_headers)
    assert list_res.status_code == 200
    tickets = list_res.get_json()["data"]
    assert any(t["id"] == ticket_id for t in tickets)

    # 3. Chủ nhà cập nhật trạng thái đang xử lý và chi phí
    update_res = client.put(
        f"/api/v1/tickets/{ticket_id}/status",
        headers=landlord_headers,
        json={"status": "resolved", "repair_cost": 85000}
    )
    assert update_res.status_code == 200
    assert update_res.get_json()["data"]["status"] == "resolved"
    assert update_res.get_json()["data"]["repair_cost"] == 85000

    # 4. Tạo và xem thông báo tòa nhà
    post_ann_res = client.post(
        "/api/v1/announcements",
        headers=landlord_headers,
        json={
            "building_id": seed_data["building"].id,
            "title": "Bảo trì thang máy",
            "content": "Thang máy bảo trì định kỳ từ 13h - 15h"
        }
    )
    assert post_ann_res.status_code == 201

    get_ann_res = client.get("/api/v1/announcements", headers=tenant_headers)
    assert get_ann_res.status_code == 200
    ann_list = get_ann_res.get_json()["data"]
    assert any("Bảo trì thang máy" in a["title"] for a in ann_list)

