"""
SAMS - VietQR Service
Tạo mã thanh toán VietQR động chuẩn EMVCo Napas247 và QuickLink ảnh QR.
Tuân thủ ADR-005: Tạo mã VietQR Offline bằng thư viện chuẩn, không phụ thuộc cổng thanh toán thứ 3.
"""
import urllib.parse
from decimal import Decimal
from flask import current_app, has_app_context


class VietQRService:
    """Service sinh mã và URL ảnh VietQR Napas247."""

    @staticmethod
    def _crc16_ccitt(data: str) -> str:
        """
        Tính mã kiểm tra CRC-16/CCITT-FALSE (poly 0x1021, init 0xFFFF).
        Quy chuẩn EMVCo Tag 63.
        """
        crc = 0xFFFF
        for char in data.encode("utf-8"):
            crc ^= char << 8
            for _ in range(8):
                if crc & 0x8000:
                    crc = ((crc << 1) ^ 0x1021) & 0xFFFF
                else:
                    crc = (crc << 1) & 0xFFFF
        return f"{crc:04X}"

    @classmethod
    def generate_emvco_payload(
        cls,
        bank_bin: str,
        account_number: str,
        amount: int | float | Decimal,
        message: str,
    ) -> str:
        """
        Tạo chuỗi payload EMVCo QR code hợp chuẩn Napas247.

        Tags:
        - 00: Payload Format Indicator (01)
        - 01: Point of Initiation Method (12 - Dynamic QR)
        - 38: Merchant Account Information (Napas GUID A000000727 + BIN + Account)
        - 53: Transaction Currency (704 - VND)
        - 54: Transaction Amount
        - 58: Country Code (VN)
        - 62: Additional Data Field (Reference / Message)
        - 63: CRC16 Checksum
        """
        amount_int = int(amount)

        # Tag 38: Napas Provider Info
        # 00: GUID Napas A000000727
        # 01: Beneficiary info (00: Bank BIN, 01: Account Number)
        # 02: Service code QRIBFTTA (Quick Transfer)
        sub_00 = f"00{len(bank_bin):02d}{bank_bin}"
        sub_01 = f"01{len(account_number):02d}{account_number}"
        napas_sub_01 = f"{sub_00}{sub_01}"
        tag_38_00 = "0010A000000727"
        tag_38_01 = f"01{len(napas_sub_01):02d}{napas_sub_01}"
        tag_38_02 = "0208QRIBFTTA"
        tag_38_content = f"{tag_38_00}{tag_38_01}{tag_38_02}"
        tag_38 = f"38{len(tag_38_content):02d}{tag_38_content}"

        # Tag 54: Amount
        str_amount = str(amount_int)
        tag_54 = f"54{len(str_amount):02d}{str_amount}" if amount_int > 0 else ""

        # Tag 62: Purpose / Message
        clean_msg = message.strip()
        sub_62_08 = f"08{len(clean_msg):02d}{clean_msg}" if clean_msg else ""
        tag_62 = f"62{len(sub_62_08):02d}{sub_62_08}" if sub_62_08 else ""

        # Assemble string before CRC
        raw_qr = (
            "000201"  # Tag 00
            "010212"  # Tag 01 (Dynamic)
            f"{tag_38}"  # Tag 38
            "5303704"  # Tag 53: 704 (VND)
            f"{tag_54}"  # Tag 54: Amount
            "5802VN"  # Tag 58: VN
            f"{tag_62}"  # Tag 62
            "6304"  # Tag 63 ID + Length
        )

        crc = cls._crc16_ccitt(raw_qr)
        return f"{raw_qr}{crc}"

    @classmethod
    def generate_vietqr_image_url(
        cls,
        bank_bin: str | None = None,
        account_number: str | None = None,
        account_name: str | None = None,
        amount: int | float | Decimal = 0,
        message: str = "",
        template: str | None = None,
    ) -> str:
        """
        Sinh URL hình ảnh mã QR qua VietQR public CDN API (chuẩn Napas247).
        Ví dụ: https://img.vietqr.io/image/970422-0987654321-compact2.png?amount=5147500&addInfo=SAMS%20P302%20T10
        """
        if has_app_context():
            bin_code = bank_bin or current_app.config.get("VIETQR_BANK_BIN", "970422")
            acc_no = account_number or current_app.config.get("VIETQR_ACCOUNT_NUMBER", "0987654321")
            acc_name = account_name or current_app.config.get("VIETQR_ACCOUNT_NAME", "")
            tpl = template or current_app.config.get("VIETQR_TEMPLATE", "compact2")
        else:
            import os
            bin_code = bank_bin or os.environ.get("VIETQR_BANK_BIN", "970422")
            acc_no = account_number or os.environ.get("VIETQR_ACCOUNT_NUMBER", "0987654321")
            acc_name = account_name or os.environ.get("VIETQR_ACCOUNT_NAME", "")
            tpl = template or os.environ.get("VIETQR_TEMPLATE", "compact2")

        amount_val = int(amount)
        base_url = f"https://img.vietqr.io/image/{bin_code}-{acc_no}-{tpl}.png"

        query_params = {}
        if amount_val > 0:
            query_params["amount"] = str(amount_val)
        if message:
            query_params["addInfo"] = message
        if acc_name:
            query_params["accountName"] = acc_name

        if query_params:
            return f"{base_url}?{urllib.parse.urlencode(query_params)}"
        return base_url
