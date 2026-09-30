"""
SAMS - Refund Service
Nghiệp vụ nghiệm thu trả phòng và quyết toán hoàn trả tiền cọc cho khách thuê.
"""
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List, Dict, Any
from flask import current_app

from app.extensions import db
from app.models.contract import Contract
from app.models.room import Room
from app.models.invoice import Invoice
from app.services.billing_service import BillingService


class RefundService:
    @staticmethod
    def preview_refund(
        contract_id: int,
        final_electricity_reading: Optional[float] = None,
        final_water_reading: Optional[float] = None,
        deductions: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Tính toán bảng dự trù quyết toán hoàn cọc trước khi xác nhận nghiệm thu."""
        contract = db.session.get(Contract, contract_id)
        if not contract:
            raise ValueError("Không tìm thấy hợp đồng thuê.")

        room = contract.room
        if not room:
            raise ValueError("Không tìm thấy thông tin phòng liên kết.")

        deposit = float(contract.deposit_amount or 0.0)

        # 1. Tính toán điện nước cuối kỳ
        now = datetime.now(timezone.utc)
        prev_elec = BillingService.get_latest_meter_reading(room.id, "electricity", before_month=now.month, before_year=now.year)
        prev_water = BillingService.get_latest_meter_reading(room.id, "water", before_month=now.month, before_year=now.year)

        prev_elec_val = float(prev_elec.reading_value) if prev_elec and prev_elec.reading_value is not None else 0.0
        prev_water_val = float(prev_water.reading_value) if prev_water and prev_water.reading_value is not None else 0.0

        elec_price = float(current_app.config.get("DEFAULT_ELECTRICITY_PRICE_PER_KWH", 3500.0))
        water_price = float(current_app.config.get("DEFAULT_WATER_PRICE_PER_M3", 25000.0))

        final_elec_val = float(final_electricity_reading) if final_electricity_reading is not None else prev_elec_val
        final_water_val = float(final_water_reading) if final_water_reading is not None else prev_water_val

        elec_consumption = max(0.0, final_elec_val - prev_elec_val)
        water_consumption = max(0.0, final_water_val - prev_water_val)

        elec_cost = round(elec_consumption * elec_price, 0)
        water_cost = round(water_consumption * water_price, 0)
        final_utility_total = elec_cost + water_cost

        # 2. Hóa đơn còn nợ (unpaid / overdue)
        unpaid_invoices = (
            db.session.query(Invoice)
            .filter(
                Invoice.contract_id == contract.id,
                Invoice.status.in_(["unpaid", "overdue", "pending_verification"])
            )
            .all()
        )
        unpaid_invoices_total = sum((float(inv.total_amount) for inv in unpaid_invoices), 0.0)

        # 3. Các khoản khấu trừ hư hao tài sản / dọn dẹp (deductions)
        deductions_list = deductions or []
        total_deductions = 0.0
        validated_deductions = []
        for d in deductions_list:
            d_desc = str(d.get("description", "Khấu trừ hư tổn")).strip()
            d_amt = float(d.get("amount", 0.0))
            if d_amt > 0:
                total_deductions += d_amt
                validated_deductions.append({"description": d_desc, "amount": d_amt})

        # 4. Số tiền cọc hoàn lại thực tế
        # refund_amount = deposit - final_utilities - unpaid_invoices - deductions
        total_subtractions = final_utility_total + unpaid_invoices_total + total_deductions
        refund_amount = deposit - total_subtractions

        return {
            "contract_id": contract.id,
            "room_id": room.id,
            "room_number": room.room_number,
            "tenant_id": contract.tenant_id,
            "initial_deposit": deposit,
            "final_utilities": {
                "electricity": {
                    "previous_reading": prev_elec_val,
                    "final_reading": final_elec_val,
                    "consumption": elec_consumption,
                    "unit_price": elec_price,
                    "cost": elec_cost,
                },
                "water": {
                    "previous_reading": prev_water_val,
                    "final_reading": final_water_val,
                    "consumption": water_consumption,
                    "unit_price": water_price,
                    "cost": water_cost,
                },
                "total_utility_cost": final_utility_total,
            },
            "unpaid_invoices": [
                {
                    "invoice_id": inv.id,
                    "month": inv.month,
                    "year": inv.year,
                    "amount": float(inv.total_amount),
                    "status": inv.status,
                }
                for inv in unpaid_invoices
            ],
            "unpaid_invoices_total": unpaid_invoices_total,
            "deductions": validated_deductions,
            "total_deductions": total_deductions,
            "total_subtractions": total_subtractions,
            "refund_amount": refund_amount,
            "is_tenant_due": refund_amount < 0,  # Nếu âm, khách thuê phải đóng thêm
        }

    @staticmethod
    def settle_refund(
        contract_id: int,
        final_electricity_reading: Optional[float] = None,
        final_water_reading: Optional[float] = None,
        deductions: Optional[List[Dict[str, Any]]] = None,
        note: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Thực hiện nghiệm thu bàn giao phòng và hoàn tất thủ tục kết thúc hợp đồng:
        1. Tính toán quyết toán.
        2. Chuyển hợp đồng sang 'terminated' và ghi thời điểm kết thúc.
        3. Giải phóng phòng: chuyển status phòng về 'vacant', xóa current_tenant_id.
        4. Đánh dấu các hóa đơn nợ đã được cấn trừ vào tiền cọc.
        """
        calculation = RefundService.preview_refund(
            contract_id=contract_id,
            final_electricity_reading=final_electricity_reading,
            final_water_reading=final_water_reading,
            deductions=deductions,
        )

        contract = db.session.get(Contract, contract_id)
        room = contract.room

        now = datetime.now(timezone.utc)

        # Cập nhật hợp đồng
        contract.status = "terminated"
        contract.terminated_at = now
        settlement_note = f"[Quyết toán hoàn cọc lúc {now.strftime('%d/%m/%Y %H:%M')}] Cọc: {calculation['initial_deposit']:,.0f}đ - Khấu trừ: {calculation['total_subtractions']:,.0f}đ => Hoàn trả: {calculation['refund_amount']:,.0f}đ."
        if note:
            settlement_note += f" Ghi chú thêm: {note.strip()}"
        contract.notes = f"{contract.notes or ''}\n{settlement_note}".strip()

        # Giải phóng phòng cho thuê
        room.status = "vacant"
        room.current_tenant_id = None

        # Đánh dấu các hóa đơn cũ là đã được thanh toán cấn trừ
        for inv_info in calculation["unpaid_invoices"]:
            inv = db.session.get(Invoice, inv_info["invoice_id"])
            if inv:
                inv.status = "paid"
                inv.paid_at = now

        db.session.commit()

        calculation["settled_at"] = now.isoformat()
        calculation["contract_status"] = contract.status
        calculation["room_status"] = room.status
        calculation["settlement_note"] = settlement_note
        return calculation
