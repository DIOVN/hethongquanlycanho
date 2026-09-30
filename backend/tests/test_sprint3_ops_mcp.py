"""
SAMS - Sprint 3 Test Suite: OpEx, Deposit Refund & FastMCP Server Tools
Kiểm thử chi phí vận hành, quyết toán hoàn cọc và 9 công cụ MCP.
"""
import sys
import os
from datetime import date, datetime, timezone
import pytest

# Đảm bảo đường dẫn root có trong sys.path để import mcp_server
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.models.room import Room, Building
from app.models.contract import Contract
from app.models.invoice import Invoice
from app.models.utility_reading import UtilityReading
from app.models.expense import Expense, ServiceTicket, BulletinAnnouncement
from app.services.expense_service import ExpenseService
from app.services.refund_service import RefundService


def test_expense_and_net_profit_service(app, seed_data):
    """Kiểm tra tạo OpEx và tính toán Lợi nhuận ròng = Doanh thu - OpEx."""
    with app.app_context():
        building = seed_data["building"]
        landlord = seed_data["landlord"]
        room = seed_data["room"]

        # 1. Tạo 1 hóa đơn đã thu (paid) = 5.000.000
        paid_inv = Invoice(
            room_id=room.id,
            month=10,
            year=2026,
            total_amount=5000000.0,
            status="paid",
            paid_at=datetime.now(timezone.utc)
        )
        app.extensions["sqlalchemy"].session.add(paid_inv)

        # 2. Tạo 2 khoản chi phí OpEx (tiền điện chung 500k, rác 200k)
        ExpenseService.create_expense(
            building_id=building.id,
            recorded_by=landlord.id,
            expense_category="common_electricity",
            title="Tiền điện chiếu sáng hành lang & bơm T10",
            amount=500000.0,
            expense_date=date(2026, 10, 15)
        )
        ExpenseService.create_expense(
            building_id=building.id,
            recorded_by=landlord.id,
            expense_category="cleaning",
            title="Dịch vụ gom rác sinh hoạt tòa nhà T10",
            amount=200000.0,
            expense_date=date(2026, 10, 16)
        )

        # 3. Lấy báo cáo tài chính
        summary = ExpenseService.get_financial_summary(month=10, year=2026, building_id=building.id)
        assert summary["total_revenue"] >= 5000000.0
        assert summary["total_opex"] >= 700000.0
        assert summary["net_profit"] == summary["total_revenue"] - summary["total_opex"]
        assert "common_electricity" in summary["category_breakdown"]


def test_deposit_refund_preview_and_settle(app, seed_data):
    """Kiểm tra quy trình nghiệm thu trả phòng và quyết toán hoàn cọc."""
    with app.app_context():
        contract = seed_data["contract"]
        room = seed_data["room"]
        initial_deposit = float(contract.deposit_amount)

        # Tạo chỉ số tháng trước: điện 100, nước 20
        now = datetime.now(timezone.utc)
        r_prev_elec = UtilityReading(
            room_id=room.id,
            meter_type="electricity",
            reading_value=100.0,
            month=now.month - 1 if now.month > 1 else 12,
            year=now.year if now.month > 1 else now.year - 1
        )
        r_prev_water = UtilityReading(
            room_id=room.id,
            meter_type="water",
            reading_value=20.0,
            month=now.month - 1 if now.month > 1 else 12,
            year=now.year if now.month > 1 else now.year - 1
        )
        app.extensions["sqlalchemy"].session.add_all([r_prev_elec, r_prev_water])
        app.extensions["sqlalchemy"].session.commit()

        # 1. Preview quyết toán
        # Chỉ số điện cuối: 150 (trước đó là 100 => dùng 50 kWh * 3500 = 175.000)
        # Chỉ số nước cuối: 25 (trước đó là 20 => dùng 5 m3 * 25000 = 125.000)
        # Khấu trừ hư hại: hỏng remote máy lạnh 200.000
        deductions = [{"description": "Hư hỏng remote máy lạnh", "amount": 200000.0}]
        preview = RefundService.preview_refund(
            contract_id=contract.id,
            final_electricity_reading=150.0,
            final_water_reading=25.0,
            deductions=deductions
        )
        expected_utilities = 175000.0 + 125000.0
        expected_deductions = 200000.0
        expected_refund = initial_deposit - (expected_utilities + expected_deductions)

        assert preview["initial_deposit"] == initial_deposit
        assert preview["final_utilities"]["total_utility_cost"] == expected_utilities
        assert preview["total_deductions"] == expected_deductions
        assert preview["refund_amount"] == expected_refund

        # 2. Thực hiện quyết toán chốt phòng (settle)
        settlement = RefundService.settle_refund(
            contract_id=contract.id,
            final_electricity_reading=150.0,
            final_water_reading=25.0,
            deductions=deductions,
            note="Khách đã dọn dẹp sạch sẽ và bàn giao 2 chìa khóa."
        )
        assert settlement["contract_status"] == "terminated"
        assert settlement["room_status"] == "vacant"

        # Kiểm tra trạng thái phòng trong database
        updated_room = app.extensions["sqlalchemy"].session.get(Room, room.id)
        assert updated_room.status == "vacant"
        assert updated_room.current_tenant_id is None


def test_expenses_and_contracts_api_flow(client, landlord_token, seed_data):
    """Kiểm tra API /expenses và /contracts/refund."""
    landlord_headers = {"Authorization": f"Bearer {landlord_token}"}
    building = seed_data["building"]

    # 1. Tạo chi phí vận hành qua API
    exp_res = client.post(
        "/api/v1/expenses",
        headers=landlord_headers,
        json={
            "building_id": building.id,
            "expense_category": "maintenance",
            "title": "Bảo dưỡng máy bơm nước định kỳ",
            "amount": 350000,
            "expense_date": "2026-10-10"
        }
    )
    assert exp_res.status_code == 201
    assert exp_res.get_json()["data"]["amount"] == 350000.0

    # 2. Xem danh sách chi phí
    list_res = client.get(f"/api/v1/expenses?building_id={building.id}", headers=landlord_headers)
    assert list_res.status_code == 200
    assert len(list_res.get_json()["data"]) >= 1

    # 3. Xem báo cáo tóm tắt tài chính
    sum_res = client.get("/api/v1/expenses/summary?month=10&year=2026", headers=landlord_headers)
    assert sum_res.status_code == 200
    assert "net_profit" in sum_res.get_json()["data"]


def test_mcp_server_tools_direct(app, seed_data):
    """Kiểm thử trực tiếp 9 Tools và 2 Resources của SAMS FastMCP Server."""
    import mcp_server.server as sams_mcp

    with app.app_context():
        # Tool 1: Revenue
        rev = sams_mcp.get_monthly_revenue(10, 2026)
        assert "total_collected_revenue" in rev

        # Tool 2: Net profit
        np = sams_mcp.get_net_profit_summary(10, 2026)
        assert "net_profit" in np

        # Tool 3: Debtor list
        debtors = sams_mcp.get_debtor_list()
        assert isinstance(debtors, list)

        # Tool 4: Occupancy report
        occ = sams_mcp.get_occupancy_report()
        assert "occupancy_rate_percent" in occ
        assert "total_rooms" in occ

        # Tool 5: Room violations
        room = seed_data["room"]
        vios = sams_mcp.get_room_violations_summary(room.id)
        assert vios["room_id"] == room.id
        assert "total_violations" in vios

        # Tool 6: Expiration forecast
        exp = sams_mcp.get_contract_expiration_forecast(365)
        assert isinstance(exp, list)

        # Tool 7: Maintenance cost
        maint = sams_mcp.get_maintenance_cost_breakdown()
        assert "total_maintenance_cost" in maint

        # Tool 8: Vacant rooms
        vacant = sams_mcp.get_vacant_rooms()
        assert isinstance(vacant, list)

        # Tool 9: Refund preview
        contract = seed_data["contract"]
        ref_prev = sams_mcp.get_refund_calculation_preview(contract.id, 120.0, 22.0, 100000.0)
        assert "refund_amount" in ref_prev

        # Resources: Rules & Bulletin
        rules = sams_mcp.get_building_rules_resource()
        assert "NỘI QUY" in rules

        bulletin = sams_mcp.get_latest_bulletin_resource()
        assert isinstance(bulletin, str)
