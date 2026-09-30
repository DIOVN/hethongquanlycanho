"""
SAMS - Expense Service
Nghiệp vụ quản lý Chi phí Vận hành (OpEx) và Báo cáo Lợi nhuận Ròng (Net Profit).
"""
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy import func, extract

from app.extensions import db
from app.models.expense import Expense
from app.models.invoice import Invoice, InvoiceItem


class ExpenseService:
    @staticmethod
    def create_expense(
        building_id: int,
        recorded_by: int,
        expense_category: str,
        title: str,
        amount: float,
        expense_date: date,
        receipt_image_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Tạo mới một khoản chi phí vận hành (OpEx)."""
        valid_categories = {
            "common_electricity",
            "water",
            "internet",
            "cleaning",
            "security",
            "maintenance",
            "other",
        }
        if expense_category not in valid_categories:
            raise ValueError(f"Danh mục chi phí không hợp lệ: {expense_category}")

        expense = Expense(
            building_id=building_id,
            recorded_by=recorded_by,
            expense_category=expense_category,
            title=title.strip(),
            amount=Decimal(str(amount)),
            expense_date=expense_date,
            receipt_image_url=receipt_image_url,
        )
        db.session.add(expense)
        db.session.commit()
        return expense.to_dict()

    @staticmethod
    def get_expenses(
        building_id: Optional[int] = None,
        month: Optional[int] = None,
        year: Optional[int] = None,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Lọc và lấy danh sách chi phí vận hành."""
        query = db.session.query(Expense)
        if building_id:
            query = query.filter(Expense.building_id == building_id)
        if month:
            query = query.filter(extract("month", Expense.expense_date) == month)
        if year:
            query = query.filter(extract("year", Expense.expense_date) == year)
        if category:
            query = query.filter(Expense.expense_category == category)

        expenses = query.order_by(Expense.expense_date.desc(), Expense.created_at.desc()).all()
        return [e.to_dict() for e in expenses]

    @staticmethod
    def get_financial_summary(month: int, year: int, building_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Tính toán Báo cáo Tài chính & Lợi nhuận Ròng:
        Lợi nhuận ròng = Doanh thu thực thu (hóa đơn đã thanh toán) - Tổng chi phí OpEx.
        """
        # 1. Doanh thu: Các hóa đơn của tháng/năm đã thanh toán ('paid')
        inv_query = db.session.query(Invoice).filter(
            Invoice.month == month,
            Invoice.year == year,
            Invoice.status == "paid"
        )
        if building_id:
            from app.models.room import Room
            inv_query = inv_query.join(Room, Invoice.room_id == Room.id).filter(Room.building_id == building_id)

        paid_invoices = inv_query.all()
        total_collected_revenue = sum((float(inv.total_amount) for inv in paid_invoices), 0.0)

        # Hóa đơn chưa thu
        unpaid_query = db.session.query(Invoice).filter(
            Invoice.month == month,
            Invoice.year == year,
            Invoice.status.in_(["unpaid", "overdue", "pending_verification"])
        )
        if building_id:
            from app.models.room import Room
            unpaid_query = unpaid_query.join(Room, Invoice.room_id == Room.id).filter(Room.building_id == building_id)

        unpaid_invoices = unpaid_query.all()
        total_pending_receivables = sum((float(inv.total_amount) for inv in unpaid_invoices), 0.0)

        # 2. Chi phí OpEx
        exp_query = db.session.query(Expense).filter(
            extract("month", Expense.expense_date) == month,
            extract("year", Expense.expense_date) == year,
        )
        if building_id:
            exp_query = exp_query.filter(Expense.building_id == building_id)

        expenses = exp_query.all()
        total_opex = sum((float(e.amount) for e in expenses), 0.0)

        # Phân loại chi phí theo danh mục
        category_breakdown: Dict[str, float] = {}
        for e in expenses:
            cat = e.expense_category
            category_breakdown[cat] = category_breakdown.get(cat, 0.0) + float(e.amount)

        # 3. Lợi nhuận ròng
        net_profit = total_collected_revenue - total_opex

        return {
            "month": month,
            "year": year,
            "building_id": building_id,
            "total_revenue": total_collected_revenue,
            "total_opex": total_opex,
            "net_profit": net_profit,
            "profit_margin_percent": round((net_profit / total_collected_revenue * 100), 2) if total_collected_revenue > 0 else 0.0,
            "pending_receivables": total_pending_receivables,
            "paid_invoices_count": len(paid_invoices),
            "unpaid_invoices_count": len(unpaid_invoices),
            "category_breakdown": category_breakdown,
        }
