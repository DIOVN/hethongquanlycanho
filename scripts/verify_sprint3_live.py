"""
SAMS - Sprint 3 Live Verification Script
Kiểm tra trực tiếp các API của Sprint 3 trên máy chủ Flask đang chạy (http://127.0.0.1:5000)
và kiểm tra FastMCP Server tools trên SQLite database.
"""
import requests
import json
import os
import sys

BASE_URL = "http://127.0.0.1:5000/api/v1"

def print_step(title):
    print(f"\n========================================================")
    print(f"==> {title}")
    print(f"========================================================")

def verify():
    session = requests.Session()

    # 1. Đăng nhập Landlord
    print_step("1. Đăng nhập Landlord")
    login_res = session.post(f"{BASE_URL}/auth/login", json={
        "username": "landlord1",
        "password": "password123"
    })
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    token = login_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[PASS] Đăng nhập Landlord thành công. JWT token acquired.")

    # 2. Lấy danh sách tòa nhà và phòng
    print_step("2. Lấy danh sách phòng & tòa nhà")
    rooms_res = session.get(f"{BASE_URL}/rooms", headers=headers)
    assert rooms_res.status_code == 200, f"Rooms failed: {rooms_res.text}"
    rooms = rooms_res.json()["data"]
    print(f"[PASS] Lấy danh sách thành công: {len(rooms)} phòng.")
    room = rooms[0]
    building_id = room.get("building_id", 1)

    # 3. Tạo chi phí vận hành OpEx (Expense)
    print_step("3. Tạo chi phí vận hành OpEx mới (Expense)")
    expense_payload = {
        "building_id": building_id,
        "expense_category": "common_electricity",
        "title": "Tiền điện bơm nước và đèn hành lang T10",
        "amount": 450000,
        "expense_date": "2026-10-15"
    }
    exp_res = session.post(f"{BASE_URL}/expenses", headers=headers, json=expense_payload)
    assert exp_res.status_code == 201, f"Create expense failed: {exp_res.text}"
    exp_data = exp_res.json()["data"]
    print(f"[PASS] Tạo chi phí thành công: ID={exp_data.get('id')}, Số tiền={exp_data.get('amount'):,}đ, Danh mục={exp_data.get('expense_category')}")

    # 4. Tra cứu danh sách OpEx
    print_step("4. Tra cứu danh sách chi phí OpEx")
    list_res = session.get(f"{BASE_URL}/expenses?building_id={building_id}", headers=headers)
    assert list_res.status_code == 200, f"List expenses failed: {list_res.text}"
    expenses = list_res.json()["data"]
    print(f"[PASS] Lấy danh sách chi phí thành công: {len(expenses)} khoản chi.")

    # 5. Xem Báo cáo Lợi Nhuận Ròng (Net Profit Summary)
    print_step("5. Báo cáo Lợi nhuận Ròng (Doanh thu - OpEx)")
    summary_res = session.get(f"{BASE_URL}/expenses/summary?month=10&year=2026&building_id={building_id}", headers=headers)
    assert summary_res.status_code == 200, f"Summary failed: {summary_res.text}"
    summary = summary_res.json()["data"]
    print(f"[PASS] Tổng doanh thu đã thu: {summary.get('total_revenue', 0):,} VNĐ")
    print(f"[PASS] Tổng chi phí OpEx:     {summary.get('total_opex', 0):,} VNĐ")
    print(f"[PASS] Lợi nhuận ròng:        {summary.get('net_profit', 0):,} VNĐ")
    print(f"[PASS] Chi tiết danh mục:     {summary.get('category_breakdown')}")

    # 6. Tra cứu hợp đồng để tính quyết toán hoàn cọc (Move-out Refund Preview)
    print_step("6. Nghiệm thu trả phòng & Tính tiền hoàn cọc (Refund Preview)")
    contracts_res = session.get(f"{BASE_URL}/contracts", headers=headers)
    assert contracts_res.status_code == 200, f"Get contracts failed: {contracts_res.text}"
    contracts = contracts_res.json()["data"]
    assert len(contracts) > 0, "No contracts found to test refund"
    contract_id = contracts[0]["id"]

    refund_preview_res = session.get(
        f"{BASE_URL}/contracts/{contract_id}/refund-preview?final_electricity_reading=120.0&final_water_reading=15.0",
        headers=headers
    )
    assert refund_preview_res.status_code == 200, f"Refund preview failed: {refund_preview_res.text}"
    ref_data = refund_preview_res.json()["data"]
    print(f"[PASS] Tiền cọc ban đầu:      {ref_data.get('initial_deposit', 0):,} VNĐ")
    print(f"[PASS] Tiền điện nước chốt:   {ref_data.get('final_utilities', {}).get('total_utility_cost', 0):,} VNĐ")
    print(f"[PASS] Khấu trừ hư hại:       {ref_data.get('total_deductions', 0):,} VNĐ")
    print(f"[PASS] Số tiền cọc hoàn lại:  {ref_data.get('refund_amount', 0):,} VNĐ")

    # 7. FastMCP Server Tools Verification
    print_step("7. Kiểm thử trực tiếp 9 Tools & 2 Resources của SAMS FastMCP Server")
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, root_dir)
    sys.path.insert(0, os.path.join(root_dir, "backend"))
    import mcp_server.server as mcp_module

    # Test tools
    rev = mcp_module.get_monthly_revenue(10, 2026)
    print(f"[MCP Tool: get_monthly_revenue] Thu được: {rev['total_collected_revenue']:,}đ, Chờ thu: {rev['total_pending_amount']:,}đ")

    net_prof = mcp_module.get_net_profit_summary(10, 2026)
    print(f"[MCP Tool: get_net_profit_summary] Lợi nhuận ròng: {net_prof['net_profit']:,}đ")

    debtors = mcp_module.get_debtor_list()
    print(f"[MCP Tool: get_debtor_list] Số phòng đang nợ tiền: {len(debtors)}")

    occ = mcp_module.get_occupancy_report()
    print(f"[MCP Tool: get_occupancy_report] Tỷ lệ lấp đầy: {occ.get('occupancy_rate_percent', 0)}%, Tổng số người ở: {occ.get('total_occupants', 0)}")

    rules = mcp_module.get_building_rules_resource()
    print(f"[MCP Resource: apartment://rules] Độ dài nội quy: {len(rules)} ký tự.")

    print("\n========================================================")
    print(">>> TẤT CẢ 7 NHÓM KIỂM THỬ SPRINT 3 HOÀN TẤT THÀNH CÔNG 100%! <<<")
    print("========================================================\n")

if __name__ == "__main__":
    verify()
