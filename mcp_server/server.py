"""
SAMS - Model Context Protocol (MCP) Server
Cung cấp 9 công cụ (Tools) và 2 tài nguyên (Resources) cho LLM Hosts (Claude Desktop, Cursor, Antigravity)
để truy vấn dữ liệu vận hành bất động sản, tài chính và cư trú theo thời gian thực.
"""
import sys
import os
from datetime import date, datetime, timedelta, timezone
from typing import Optional, List, Dict, Any

# Thêm đường dẫn backend vào sys.path để import models và services của Flask
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, ".env"))

from fastmcp import FastMCP

# Khởi tạo FastMCP Server
mcp = FastMCP("SAMS-Apartment-Intelligence")

# Import Flask App để truy cập SQLAlchemy Models trong Application Context
from app import create_app
from app.extensions import db
from app.models.room import Room, Building
from app.models.contract import Contract
from app.models.invoice import Invoice
from app.models.expense import Expense, ServiceTicket, BulletinAnnouncement
from app.models.violation import RoomViolation
from app.models.roommate import Roommate
from app.services.expense_service import ExpenseService
from app.services.refund_service import RefundService

flask_app = create_app()


# ==============================================================================
# MCP TOOLS (9 TOOLS CHUYÊN BIỆT CHO CHỦ CĂN HỘ / QUẢN LÝ)
# ==============================================================================

@mcp.tool()
def get_monthly_revenue(month: int, year: int) -> Dict[str, Any]:
    """
    Tra cứu tổng doanh thu hóa đơn thực thu của các phòng trong tháng và năm chỉ định.
    
    Args:
        month: Tháng cần xem (1-12)
        year: Năm cần xem (VD: 2026)
    """
    with flask_app.app_context():
        paid_invoices = (
            db.session.query(Invoice)
            .filter(Invoice.month == month, Invoice.year == year, Invoice.status == "paid")
            .all()
        )
        total_rev = sum((float(inv.total_amount) for inv in paid_invoices), 0.0)
        
        unpaid_invoices = (
            db.session.query(Invoice)
            .filter(
                Invoice.month == month,
                Invoice.year == year,
                Invoice.status.in_(["unpaid", "overdue", "pending_verification"])
            )
            .all()
        )
        total_pending = sum((float(inv.total_amount) for inv in unpaid_invoices), 0.0)

        return {
            "month": month,
            "year": year,
            "total_collected_revenue": total_rev,
            "paid_count": len(paid_invoices),
            "total_pending_amount": total_pending,
            "unpaid_count": len(unpaid_invoices),
        }


@mcp.tool()
def get_net_profit_summary(month: int, year: int, building_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Tính toán báo cáo lợi nhuận ròng: Lợi nhuận ròng = Doanh thu thực thu - Chi phí vận hành OpEx.
    
    Args:
        month: Tháng cần xem (1-12)
        year: Năm cần xem (VD: 2026)
        building_id: Mã tòa nhà (tùy chọn)
    """
    with flask_app.app_context():
        return ExpenseService.get_financial_summary(month=month, year=year, building_id=building_id)


@mcp.tool()
def get_debtor_list() -> List[Dict[str, Any]]:
    """
    Liệt kê danh sách các phòng còn nợ tiền hóa đơn chưa thanh toán hoặc quá hạn.
    Cung cấp số phòng, tên khách thuê, số điện thoại, số tiền nợ và mã tham chiếu.
    """
    with flask_app.app_context():
        unpaid = (
            db.session.query(Invoice)
            .filter(Invoice.status.in_(["unpaid", "overdue", "pending_verification"]))
            .order_by(Invoice.year.asc(), Invoice.month.asc())
            .all()
        )
        debtors = []
        for inv in unpaid:
            room = inv.room
            tenant = inv.contract.tenant if inv.contract else None
            debtors.append({
                "invoice_id": inv.id,
                "room_id": inv.room_id,
                "room_number": room.room_number if room else "N/A",
                "tenant_name": tenant.full_name if tenant else "N/A",
                "tenant_phone": tenant.phone if tenant else "N/A",
                "month": inv.month,
                "year": inv.year,
                "amount": float(inv.total_amount),
                "status": inv.status,
                "payment_ref": inv.payment_ref,
                "due_date": inv.due_date.isoformat() if inv.due_date else None,
            })
        return debtors


@mcp.tool()
def get_occupancy_report(building_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Báo cáo tỷ lệ lấp đầy phòng, số lượng phòng trống, số hợp đồng đang thuê và tổng số nhân khẩu/người ở ghép.
    
    Args:
        building_id: Mã tòa nhà cần lọc (tùy chọn)
    """
    with flask_app.app_context():
        query = db.session.query(Room)
        if building_id:
            query = query.filter(Room.building_id == building_id)
        
        rooms = query.all()
        total_rooms = len(rooms)
        occupied_rooms = sum(1 for r in rooms if r.status == "occupied" or r.current_tenant_id)
        vacant_rooms = sum(1 for r in rooms if r.status == "vacant")
        maintenance_rooms = sum(1 for r in rooms if r.status == "maintenance")

        # Đếm tổng nhân khẩu đang cư trú (Primary tenants + Roommates)
        total_roommates = db.session.query(Roommate).count()
        total_headcount = occupied_rooms + total_roommates

        occupancy_rate = round((occupied_rooms / total_rooms * 100), 2) if total_rooms > 0 else 0.0

        return {
            "total_rooms": total_rooms,
            "occupied_rooms": occupied_rooms,
            "vacant_rooms": vacant_rooms,
            "maintenance_rooms": maintenance_rooms,
            "occupancy_rate_percent": occupancy_rate,
            "total_resident_headcount": total_headcount,
            "total_registered_roommates": total_roommates,
        }


@mcp.tool()
def get_room_violations_summary(room_id: int) -> Dict[str, Any]:
    """
    Tra cứu tổng hợp lịch sử các vụ vi phạm nội quy của một phòng cụ thể (tiếng ồn, rác thải, PCCC, ở ghép, hút thuốc).
    
    Args:
        room_id: ID phòng cần tra cứu
    """
    with flask_app.app_context():
        violations = (
            db.session.query(RoomViolation)
            .filter(RoomViolation.room_id == room_id)
            .order_by(RoomViolation.created_at.desc())
            .all()
        )
        total_penalties = sum((float(v.penalty_amount) for v in violations if v.penalty_amount), 0.0)
        
        breakdown = {}
        for v in violations:
            breakdown[v.violation_type] = breakdown.get(v.violation_type, 0) + 1

        return {
            "room_id": room_id,
            "total_violations": len(violations),
            "total_penalties_amount": total_penalties,
            "violations_by_type": breakdown,
            "recent_cases": [v.to_dict() for v in violations[:5]],
        }


@mcp.tool()
def get_contract_expiration_forecast(days: int = 60) -> List[Dict[str, Any]]:
    """
    Dự báo các hợp đồng thuê phòng sẽ hết hạn trong số ngày tới để chủ nhà chủ động tái ký hoặc tìm khách mới.
    
    Args:
        days: Số ngày tới cần quét (mặc định 60 ngày)
    """
    with flask_app.app_context():
        today = date.today()
        target_date = today + timedelta(days=days)
        
        contracts = (
            db.session.query(Contract)
            .filter(
                Contract.status == "active",
                Contract.end_date >= today,
                Contract.end_date <= target_date,
            )
            .order_by(Contract.end_date.asc())
            .all()
        )
        results = []
        for c in contracts:
            room = c.room
            tenant = c.tenant
            days_left = (c.end_date - today).days
            results.append({
                "contract_id": c.id,
                "room_id": c.room_id,
                "room_number": room.room_number if room else "N/A",
                "tenant_name": tenant.full_name if tenant else "N/A",
                "tenant_phone": tenant.phone if tenant else "N/A",
                "monthly_rent": float(c.monthly_rent) if c.monthly_rent else 0.0,
                "deposit_amount": float(c.deposit_amount) if c.deposit_amount else 0.0,
                "end_date": c.end_date.isoformat(),
                "days_remaining": days_left,
            })
        return results


@mcp.tool()
def get_maintenance_cost_breakdown(month: Optional[int] = None, year: Optional[int] = None) -> Dict[str, Any]:
    """
    Thống kê tổng chi phí bảo trì, sửa chữa kỹ thuật đã giải quyết và phân loại theo hạng mục (điện, nước, gia dụng).
    """
    with flask_app.app_context():
        query = db.session.query(ServiceTicket).filter(
            ServiceTicket.status == "resolved",
            ServiceTicket.repair_cost > 0
        )
        tickets = query.all()
        total_cost = sum((float(t.repair_cost) for t in tickets if t.repair_cost), 0.0)

        by_category: Dict[str, float] = {}
        for t in tickets:
            cat = t.category or "other"
            by_category[cat] = by_category.get(cat, 0.0) + float(t.repair_cost or 0.0)

        return {
            "total_maintenance_cost": total_cost,
            "resolved_tickets_count": len(tickets),
            "cost_by_category": by_category,
        }


@mcp.tool()
def get_vacant_rooms() -> List[Dict[str, Any]]:
    """
    Tra cứu danh sách các phòng còn trống sẵn sàng cho thuê ngay cùng thông tin tầng, giá thuê và tiện nghi.
    """
    with flask_app.app_context():
        rooms = (
            db.session.query(Room)
            .filter(Room.status == "vacant")
            .order_by(Room.floor.asc(), Room.room_number.asc())
            .all()
        )
        return [r.to_dict() for r in rooms]


@mcp.tool()
def get_refund_calculation_preview(
    contract_id: int,
    final_elec: Optional[float] = None,
    final_water: Optional[float] = None,
    damages_amount: float = 0.0,
) -> Dict[str, Any]:
    """
    Tính toán chi tiết khoản hoàn trả tiền cọc cho khách thuê khi chuẩn bị trả phòng (Move-out Refund).
    
    Args:
        contract_id: ID hợp đồng thuê cần quyết toán
        final_elec: Chỉ số điện cuối cùng khi dọn ra
        final_water: Chỉ số nước cuối cùng khi dọn ra
        damages_amount: Tổng chi phí trừ hư hỏng đồ đạc / dọn dẹp
    """
    with flask_app.app_context():
        deductions = []
        if damages_amount > 0:
            deductions.append({"description": "Khấu trừ hư tổn tài sản / dọn vệ sinh", "amount": damages_amount})
        
        return RefundService.preview_refund(
            contract_id=contract_id,
            final_electricity_reading=final_elec,
            final_water_reading=final_water,
            deductions=deductions,
        )


# ==============================================================================
# MCP RESOURCES (TÀI NGUYÊN NỘI QUY & THÔNG BÁO)
# ==============================================================================

@mcp.resource("apartment://rules")
def get_building_rules_resource() -> str:
    """Tài nguyên văn bản quy chế & nội quy chính thức của tòa nhà căn hộ SAMS."""
    return """=== NỘI QUY TÒA NHÀ CĂN HỘ THÔNG MINH SAMS ===
1. GIỜ GIẤC & AN NINH CỬA CỔNG:
   - Cổng chính tự động khóa vào lúc 23h00 đêm và mở lại vào lúc 05h00 sáng.
   - Cư dân ra vào sau 23h00 vui lòng dùng vân tay/thẻ từ hoặc báo trước cho quản lý.
2. TRẬT TỰ & TIẾNG ỒN:
   - Nghiêm cấm hát karaoke, mở loa công suất lớn, tiệc tùng gây ồn sau 22h00.
3. VỆ SINH MÔI TRƯỜNG:
   - Rác sinh hoạt phải được buộc kín trong bao và để tại thùng rác trung tâm tầng trệt.
   - Không để giày dép, túi rác, đồ dùng cá nhân cản trở lối đi hành lang và cầu thang thoát hiểm.
4. AN TOÀN PHÒNG CHÁY CHỮA CHÁY (PCCC):
   - Tuyệt đối cấm hút thuốc trong thang máy, phòng kín máy lạnh và khu vực để xe.
   - Không tự ý sạc xe máy điện qua đêm ngoài khu vực sạc chuyên dụng được cấp phép.
5. KHÁCH ĐẾN THĂM & Ở GHÉP:
   - Người thân/bạn bè ở lại qua đêm (sau 23h00) phải khai báo thông tin tạm trú với Quản lý tòa nhà."""


@mcp.resource("apartment://bulletin-latest")
def get_latest_bulletin_resource() -> str:
    """Tài nguyên 5 thông báo mới nhất trên bảng tin tòa nhà."""
    with flask_app.app_context():
        announcements = (
            db.session.query(BulletinAnnouncement)
            .order_by(BulletinAnnouncement.created_at.desc())
            .limit(5)
            .all()
        )
        if not announcements:
            return "Hiện tại không có thông báo mới trên bảng tin."
        
        lines = ["=== BẢNG TIN TÒA NHÀ SAMS MỚI NHẤT ==="]
        for a in announcements:
            lines.append(f"[{a.created_at.strftime('%d/%m/%Y')}] {a.title} ({a.priority}): {a.content}")
        return "\n\n".join(lines)


if __name__ == "__main__":
    # Khởi chạy FastMCP server qua stdio (hoặc SSE)
    mcp.run()
