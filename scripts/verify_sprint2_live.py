import io
import requests

BASE = "http://127.0.0.1:5000/api/v1"

print("--- 1. Authenticating Landlord & Tenant ---")
res_ll = requests.post(f"{BASE}/auth/login", json={"username": "landlord1", "password": "password123"})
assert res_ll.status_code == 200, f"Landlord login failed: {res_ll.text}"
ll_token = res_ll.json()["data"]["access_token"]
ll_headers = {"Authorization": f"Bearer {ll_token}"}
print("  Landlord login: OK")

res_tn = requests.post(f"{BASE}/auth/login", json={"username": "tenant1", "password": "password123"})
assert res_tn.status_code == 200, f"Tenant login failed: {res_tn.text}"
tn_token = res_tn.json()["data"]["access_token"]
tn_headers = {"Authorization": f"Bearer {tn_token}"}
print("  Tenant login: OK")

print("\n--- 2. Testing Meter OCR Scan (/meters/scan-reading) ---")
dummy_img = io.BytesIO(b"fake-meter-image-content-for-ocr")
files = {"image": ("meter.jpg", dummy_img, "image/jpeg")}
data = {"room_id": "1", "meter_type": "electricity"}
res_ocr = requests.post(f"{BASE}/meters/scan-reading", headers=ll_headers, files=files, data=data)
assert res_ocr.status_code == 200, f"OCR failed: {res_ocr.text}"
ocr_data = res_ocr.json()["data"]
print(f"  OCR Result: detected_reading={ocr_data['detected_reading']}, confidence={ocr_data['confidence']}")

print("\n--- 3. Testing Violations API (/violations) ---")
res_vio = requests.post(
    f"{BASE}/violations",
    headers=ll_headers,
    json={
        "room_id": 1,
        "violation_type": "noise",
        "title": "Hát karaoke sau 22h gây ồn",
        "description": "Căn hộ hàng xóm phản ánh ồn ào lúc 23h30",
    }
)
assert res_vio.status_code == 201, f"Create violation failed: {res_vio.text}"
vio_data = res_vio.json()["data"]
print(f"  Recorded Violation ID={vio_data['violation_id']}, severity={vio_data['severity']}, penalty={vio_data['penalty_amount']} VND")

print("\n--- 4. Testing Quick Invoicing (/quick-invoices) ---")
res_inv = requests.post(
    f"{BASE}/quick-invoices",
    headers=ll_headers,
    data={
        "room_id": "1",
        "month": "11",
        "year": "2026",
        "electricity_reading": "120",
        "water_reading": "15"
    }
)
assert res_inv.status_code == 201, f"Quick invoice failed: {res_inv.text}"
inv_data = res_inv.json()["data"]
print(f"  Created Invoice #{inv_data['invoice_id']}: total={inv_data['total_amount']} VND, status={inv_data['status']}")
if inv_data.get("penalties_attached"):
    print(f"  Penalties attached: {len(inv_data['penalties_attached'])} items")

print("\n--- 5. Testing Tenant My Invoices (/billing/my-invoices) ---")
res_my_inv = requests.get(f"{BASE}/billing/my-invoices", headers=tn_headers)
assert res_my_inv.status_code == 200, f"My invoices failed: {res_my_inv.text}"
my_invoices = res_my_inv.json()["data"]
print(f"  Tenant has {len(my_invoices)} invoices. Latest VietQR link available.")

print("\n--- 6. Testing AI Chat Assistant with VietQR Action (/chat/message) ---")
res_chat = requests.post(
    f"{BASE}/chat/message",
    headers=tn_headers,
    json={"message": "Tôi muốn hỏi tiền phòng tháng này bao nhiêu để thanh toán?"}
)
assert res_chat.status_code == 200, f"Chat failed: {res_chat.text}"
chat_data = res_chat.json()["data"]
print(f"  AI Reply: {chat_data['reply'][:90]}...")
if chat_data.get("attached_action"):
    print(f"  Function called: {chat_data.get('function_called')}")
    print(f"  Attached Action: {chat_data['attached_action']['type']}, VietQR URL generated: {bool(chat_data['attached_action'].get('vietqr_url'))}")

print("\n--- 7. Testing Service Tickets (/tickets) ---")
res_ticket = requests.post(
    f"{BASE}/tickets",
    headers=tn_headers,
    json={
        "room_id": 1,
        "title": "Bồn rửa chén bị nghẹt nước",
        "category": "plumbing",
        "priority": "medium",
        "description": "Nước thoát rất chậm từ tối qua"
    }
)
assert res_ticket.status_code == 201, f"Create ticket failed: {res_ticket.text}"
ticket_id = res_ticket.json()["data"]["id"]
print(f"  Created Ticket ID={ticket_id}, status={res_ticket.json()['data']['status']}")

res_upd_ticket = requests.put(
    f"{BASE}/tickets/{ticket_id}/status",
    headers=ll_headers,
    json={"status": "in_progress", "repair_cost": 50000}
)
assert res_upd_ticket.status_code == 200
print(f"  Updated Ticket: status={res_upd_ticket.json()['data']['status']}, repair_cost={res_upd_ticket.json()['data']['repair_cost']} VND")

print("\n--- 8. Testing Bulletin Announcements (/announcements) ---")
res_ann = requests.post(
    f"{BASE}/announcements",
    headers=ll_headers,
    json={
        "building_id": 1,
        "title": "Bảo trì định kỳ máy bơm nước",
        "content": "Khu vực tầng hầm bảo trì máy bơm từ 8h00 - 10h00 sáng mai",
        "priority": "important"
    }
)
assert res_ann.status_code == 201, f"Announcements failed: {res_ann.text}"
print(f"  Created Announcement ID={res_ann.json()['data']['id']}, title='{res_ann.json()['data']['title']}'")

print("\n=======================================================")
print(" ALL SPRINT 2 ENDPOINTS VERIFIED AND RESPONDING 200/201 OK!")
print("=======================================================")
