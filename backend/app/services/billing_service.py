"""
SAMS - Billing & Quick Invoicing Service
Nghiệp vụ tính toán hóa đơn, chốt chỉ số điện nước, sinh mã VietQR và kiểm soát công nợ.
Tuân thủ FR-LANDLORD-07 và FR-TENANT-06.
"""
from datetime import datetime, date, timezone
from decimal import Decimal
from typing import Any

from flask import current_app
from app.extensions import db
from app.models.room import Room
from app.models.contract import Contract
from app.models.invoice import Invoice, InvoiceItem
from app.models.utility_reading import UtilityReading
from app.services.vietqr_service import VietQRService
from app.services.violation_service import ViolationService


class BillingService:
    """Service xử lý toàn bộ logic tính tiền, xuất hóa đơn và thanh toán VietQR."""

    @classmethod
    def get_latest_meter_reading(
        cls, room_id: int, meter_type: str, before_month: int | None = None, before_year: int | None = None
    ) -> UtilityReading | None:
        """Lấy chỉ số công tơ gần nhất của phòng để làm mốc tính tiêu thụ."""
        query = (
            db.session.query(UtilityReading)
            .filter(
                UtilityReading.room_id == room_id,
                UtilityReading.meter_type == meter_type,
            )
        )
        if before_month and before_year:
            # Lọc các kỳ trước
            query = query.filter(
                (UtilityReading.year < before_year)
                | ((UtilityReading.year == before_year) & (UtilityReading.month < before_month))
            )
        return query.order_by(UtilityReading.year.desc(), UtilityReading.month.desc(), UtilityReading.id.desc()).first()

    @classmethod
    def record_utility_reading(
        cls,
        room_id: int,
        meter_type: str,
        reading_value: float | Decimal,
        month: int,
        year: int,
        image_proof_url: str | None = None,
        ai_confidence: float | None = None,
    ) -> UtilityReading:
        """
        Ghi nhận chỉ số đo đạc điện hoặc nước của phòng vào database.
        Tự động so sánh với chỉ số kỳ trước để tính sản lượng tiêu thụ.
        """
        reading_dec = Decimal(str(reading_value))

        # Tìm chỉ số kỳ trước
        prev = cls.get_latest_meter_reading(room_id, meter_type, before_month=month, before_year=year)
        prev_value = Decimal(str(prev.reading_value)) if prev and prev.reading_value is not None else Decimal("0.0")

        # Cờ bất thường nếu số mới thấp hơn số cũ
        flag_abnormal = reading_dec < prev_value
        consumption = max(Decimal("0.0"), reading_dec - prev_value) if not flag_abnormal else Decimal("0.0")

        # Kiểm tra xem đã có bản ghi cho kỳ này chưa
        existing = (
            db.session.query(UtilityReading)
            .filter_by(room_id=room_id, meter_type=meter_type, month=month, year=year)
            .first()
        )
        if existing:
            existing.reading_value = reading_dec
            existing.previous_value = prev_value
            existing.consumption = consumption
            if image_proof_url:
                existing.image_proof_url = image_proof_url
            if ai_confidence is not None:
                existing.ai_confidence = ai_confidence
            existing.flag_abnormal = flag_abnormal
            existing.recorded_at = datetime.now(timezone.utc)
            db.session.commit()
            return existing

        reading = UtilityReading(
            room_id=room_id,
            meter_type=meter_type,
            reading_value=reading_dec,
            previous_value=prev_value,
            consumption=consumption,
            image_proof_url=image_proof_url,
            ai_confidence=ai_confidence,
            flag_abnormal=flag_abnormal,
            month=month,
            year=year,
        )
        db.session.add(reading)
        db.session.commit()
        return reading

    @classmethod
    def create_quick_invoice(
        cls,
        room_id: int,
        month: int,
        year: int,
        electricity_reading: float | Decimal | None = None,
        water_reading: float | Decimal | None = None,
        electricity_image_url: str | None = None,
        water_image_url: str | None = None,
        electricity_confidence: float | None = None,
        water_confidence: float | None = None,
    ) -> dict[str, Any]:
        """
        Tạo hóa đơn nhanh (Quick Invoice) tại chỗ khi chủ nhà đi kiểm tra phòng.
        Tự động tính tiền điện, nước, phòng, dịch vụ và cộng gộp các khoản phạt vi phạm tồn đọng.
        """
        room = db.session.get(Room, room_id)
        if not room:
            raise ValueError(f"Không tìm thấy phòng với ID {room_id}")

        # Lấy hợp đồng còn hiệu lực (nếu có)
        active_contract = (
            db.session.query(Contract)
            .filter(
                Contract.room_id == room_id,
                Contract.status == "active",
            )
            .first()
        )

        # Kiểm tra xem hóa đơn tháng này của phòng đã lập chưa
        existing_invoice = (
            db.session.query(Invoice)
            .filter_by(room_id=room_id, month=month, year=year)
            .first()
        )
        if existing_invoice and existing_invoice.status == "paid":
            raise ValueError(f"Hóa đơn tháng {month}/{year} của phòng {room.room_number} đã được thanh toán.")

        # Xóa hóa đơn cũ chưa thanh toán nếu tạo lại
        if existing_invoice:
            db.session.delete(existing_invoice)
            db.session.flush()

        # 1. Ghi nhận chỉ số điện nước nếu có
        elec_reading_obj = None
        water_reading_obj = None

        if electricity_reading is not None:
            elec_reading_obj = cls.record_utility_reading(
                room_id=room_id,
                meter_type="electricity",
                reading_value=electricity_reading,
                month=month,
                year=year,
                image_proof_url=electricity_image_url,
                ai_confidence=electricity_confidence,
            )

        if water_reading is not None:
            water_reading_obj = cls.record_utility_reading(
                room_id=room_id,
                meter_type="water",
                reading_value=water_reading,
                month=month,
                year=year,
                image_proof_url=water_image_url,
                ai_confidence=water_confidence,
            )

        # Đơn giá từ config
        elec_price = Decimal(str(current_app.config.get("DEFAULT_ELECTRICITY_PRICE_PER_KWH", 3500)))
        water_price = Decimal(str(current_app.config.get("DEFAULT_WATER_PRICE_PER_M3", 25000)))
        internet_fee = Decimal(str(current_app.config.get("DEFAULT_INTERNET_FEE_PER_ROOM", 100000)))
        cleaning_fee = Decimal(str(current_app.config.get("DEFAULT_CLEANING_FEE_PER_ROOM", 50000)))

        # Tiền phòng
        rent_amount = (
            Decimal(str(active_contract.monthly_rent))
            if active_contract and active_contract.monthly_rent
            else (Decimal(str(room.base_price)) if room.base_price else Decimal("4500000.00"))
        )

        # Tạo đối tượng Invoice
        # Ngày hết hạn thanh toán mặc định: ngày 5 của tháng tiếp theo
        due_month = month + 1 if month < 12 else 1
        due_year = year if month < 12 else year + 1
        due_date_val = date(due_year, due_month, 5)

        invoice = Invoice(
            room_id=room_id,
            contract_id=active_contract.id if active_contract else None,
            month=month,
            year=year,
            total_amount=Decimal("0.00"),
            status="unpaid",
            due_date=due_date_val,
            created_at=datetime.now(timezone.utc),
        )
        db.session.add(invoice)
        db.session.flush()

        items = []

        # Mục 1: Tiền thuê phòng
        item_rent = InvoiceItem(
            invoice_id=invoice.id,
            item_type="rent",
            description=f"Tiền phòng T{month:02d}/{year}",
            unit_price=rent_amount,
            quantity=Decimal("1.0"),
            subtotal=rent_amount,
        )
        items.append(item_rent)

        # Mục 2: Tiền điện
        if elec_reading_obj:
            elec_kwh = Decimal(str(elec_reading_obj.consumption or 0))
            elec_subtotal = elec_kwh * elec_price
            item_elec = InvoiceItem(
                invoice_id=invoice.id,
                item_type="electricity",
                description=f"Điện: {float(elec_kwh):g} kWh (CS: {float(elec_reading_obj.reading_value):g} - {float(elec_reading_obj.previous_value):g}) x {int(elec_price):,}đ",
                unit_price=elec_price,
                quantity=elec_kwh,
                subtotal=elec_subtotal,
            )
            items.append(item_elec)

        # Mục 3: Tiền nước
        if water_reading_obj:
            water_m3 = Decimal(str(water_reading_obj.consumption or 0))
            water_subtotal = water_m3 * water_price
            item_water = InvoiceItem(
                invoice_id=invoice.id,
                item_type="water",
                description=f"Nước: {float(water_m3):g} m3 (CS: {float(water_reading_obj.reading_value):g} - {float(water_reading_obj.previous_value):g}) x {int(water_price):,}đ",
                unit_price=water_price,
                quantity=water_m3,
                subtotal=water_subtotal,
            )
            items.append(item_water)

        # Mục 4: Phí dịch vụ Internet & Rác
        service_subtotal = internet_fee + cleaning_fee
        item_service = InvoiceItem(
            invoice_id=invoice.id,
            item_type="service",
            description=f"Internet ({int(internet_fee):,}đ) & Vệ sinh rác ({int(cleaning_fee):,}đ)",
            unit_price=service_subtotal,
            quantity=Decimal("1.0"),
            subtotal=service_subtotal,
        )
        items.append(item_service)

        # Mục 5: Tiền phạt vi phạm nội quy tồn đọng
        pending_penalties = ViolationService.get_pending_penalties(room_id)
        for p in pending_penalties:
            p_subtotal = Decimal(str(p.penalty_amount or 0))
            if p_subtotal > 0:
                item_penalty = InvoiceItem(
                    invoice_id=invoice.id,
                    item_type="penalty",
                    description=f"Phạt vi phạm: {p.title} (Biên bản #{p.id})",
                    unit_price=p_subtotal,
                    quantity=Decimal("1.0"),
                    subtotal=p_subtotal,
                )
                items.append(item_penalty)
                db.session.flush()
                # Cập nhật trạng thái vi phạm sang penalized
                p.status = "penalized"
                p.invoice_item_id = item_penalty.id

        db.session.add_all(items)

        # Tính tổng tiền
        total_sum = sum((item.subtotal for item in items), Decimal("0.00"))
        invoice.total_amount = total_sum

        # Nội dung chuyển khoản: SAMS P{room_number} T{month}
        clean_room_num = room.room_number.replace(" ", "")
        payment_ref = f"SAMS P{clean_room_num} T{month}"
        invoice.payment_ref = payment_ref

        # Sinh mã VietQR
        bank_bin = current_app.config.get("VIETQR_BANK_BIN", "970422")
        acc_no = current_app.config.get("VIETQR_ACCOUNT_NUMBER", "0987654321")
        acc_name = current_app.config.get("VIETQR_ACCOUNT_NAME", "CHU NHA")
        template = current_app.config.get("VIETQR_TEMPLATE", "compact2")

        emvco_payload = VietQRService.generate_emvco_payload(
            bank_bin=bank_bin,
            account_number=acc_no,
            amount=total_sum,
            message=payment_ref,
        )
        invoice.vietqr_payload = emvco_payload

        db.session.commit()

        # Tạo URL ảnh VietQR
        vietqr_url = VietQRService.generate_vietqr_image_url(
            bank_bin=bank_bin,
            account_number=acc_no,
            account_name=acc_name,
            amount=total_sum,
            message=payment_ref,
            template=template,
        )

        return {
            "invoice_id": invoice.id,
            "room_id": room.id,
            "room_number": room.room_number,
            "month": invoice.month,
            "year": invoice.year,
            "total_amount": float(total_sum),
            "status": invoice.status,
            "payment_ref": payment_ref,
            "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
            "vietqr_url": vietqr_url,
            "vietqr_payload": emvco_payload,
            "items": [it.to_dict() for it in items],
            "evidence_images": {
                "electricity_meter": elec_reading_obj.image_proof_url if elec_reading_obj else None,
                "water_meter": water_reading_obj.image_proof_url if water_reading_obj else None,
            },
        }

    @classmethod
    def get_invoices(
        cls,
        room_id: int | None = None,
        month: int | None = None,
        year: int | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        """Lấy danh sách hóa đơn theo các điều kiện lọc."""
        query = db.session.query(Invoice)

        if room_id:
            query = query.filter(Invoice.room_id == room_id)
        if month:
            query = query.filter(Invoice.month == month)
        if year:
            query = query.filter(Invoice.year == year)
        if status:
            query = query.filter(Invoice.status == status)

        invoices = query.order_by(Invoice.year.desc(), Invoice.month.desc(), Invoice.id.desc()).all()
        results = []
        for inv in invoices:
            data = inv.to_dict(include_items=True)
            if inv.room:
                data["room_number"] = inv.room.room_number
                data["building_name"] = inv.room.building.name if inv.room.building else None
            # Sinh URL ảnh VietQR
            data["vietqr_image_url"] = VietQRService.generate_vietqr_image_url(
                amount=inv.total_amount,
                message=inv.payment_ref or f"SAMS P{inv.room_id} T{inv.month}",
            )
            results.append(data)
        return results

    @classmethod
    def get_invoice_by_id(cls, invoice_id: int) -> dict[str, Any] | None:
        """Lấy thông tin chi tiết một hóa đơn theo ID kèm các dòng mục và VietQR URL."""
        inv = db.session.get(Invoice, invoice_id)
        if not inv:
            return None
        data = inv.to_dict(include_items=True)
        if inv.room:
            data["room_number"] = inv.room.room_number
            data["building_name"] = inv.room.building.name if inv.room.building else None
        data["vietqr_image_url"] = VietQRService.generate_vietqr_image_url(
            amount=inv.total_amount,
            message=inv.payment_ref or f"SAMS P{inv.room_id} T{inv.month}",
        )
        return data

    @classmethod
    def upload_payment_slip(cls, invoice_id: int, slip_url: str) -> dict[str, Any]:
        """Khách tải ảnh chụp biên lai giao dịch chuyển khoản ngân hàng."""
        inv = db.session.get(Invoice, invoice_id)
        if not inv:
            raise ValueError(f"Không tìm thấy hóa đơn ID {invoice_id}")

        inv.payment_slip_url = slip_url
        inv.status = "pending_verification"
        db.session.commit()

        return {
            "invoice_id": inv.id,
            "status": inv.status,
            "payment_slip_url": inv.payment_slip_url,
            "submitted_at": datetime.now(timezone.utc).isoformat(),
        }

    @classmethod
    def confirm_payment(cls, invoice_id: int) -> dict[str, Any]:
        """Chủ nhà xác nhận đã nhận được tiền và đánh dấu hóa đơn đã thanh toán."""
        inv = db.session.get(Invoice, invoice_id)
        if not inv:
            raise ValueError(f"Không tìm thấy hóa đơn ID {invoice_id}")

        inv.status = "paid"
        inv.paid_at = datetime.now(timezone.utc)
        db.session.commit()

        return inv.to_dict(include_items=True)
