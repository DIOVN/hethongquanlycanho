"""
SAMS - Gemini AI Chat Assistant Service
Trợ lý ảo 24/7 phục vụ cư dân và khách thuê tòa nhà.
Tích hợp Function Calling, tra cứu tiền phòng, giải đáp nội quy và tiếp nhận báo hỏng.
Tuân thủ FR-AI-01, FR-AI-02, FR-AI-03.
"""
import json
import logging
import os
from typing import Any
from flask import current_app

from app.extensions import db
from app.models.room import Room
from app.models.contract import Contract
from app.models.invoice import Invoice
from app.models.expense import BulletinAnnouncement
from app.models.chat_session import ChatSession
from app.services.vietqr_service import VietQRService

logger = logging.getLogger(__name__)

# Nội quy chuẩn của tòa nhà căn hộ SAMS
BUILDING_RULES = """
=== NỘI QUY TÒA NHÀ CĂN HỘ SAMS ===
1. GIỜ GIẤC & AN NINH TRẬT TỰ:
   - Giờ đóng cổng chính: 23:00 hàng ngày. Cư dân về muộn vui lòng dùng vân tay/thẻ từ và đóng chặt cổng.
   - Giữ yên lặng chung sau 22:00. Nghiêm cấm hát karaoke, mở loa công suất lớn, nhậu nhẹt gây ồn ào ảnh hưởng phòng xung quanh.
2. VỆ SINH CHUNG:
   - Rác sinh hoạt phải được buộc kín trong bao và bỏ vào thùng rác tầng trệt trước 08:00 sáng.
   - Không để rác, giày dép bừa bãi trước cửa phòng hoặc ngoài hành lang chung.
3. AN TOÀN PCCC & THIẾT BỊ ĐIỆN:
   - Tuyệt đối không sạc pin xe điện qua đêm ở khu vực cấm.
   - Tắt tất cả thiết bị điện không cần thiết và khóa van gas khi ra khỏi phòng.
4. QUY ĐỊNH LƯU TRÚ & BẠN CÙNG PHÒNG:
   - Khách đến chơi qua đêm phải khai báo với ban quản lý trước 21:00 để làm thủ tục tạm trú công an.
   - Không được tự ý cho người lạ ở ghép vượt quá số lượng đăng ký trong hợp đồng.
5. KHÔNG HÚT THUỐC:
   - Cấm hút thuốc lá, thuốc lá điện tử trong thang máy, hành lang và các khu vực sinh hoạt chung.
"""


class GeminiChatService:
    """Service xử lý đàm thoại trợ lý ảo Gemini cho cư dân."""

    @staticmethod
    def _log_chat(user_id: int, room_id: int | None, user_msg: str, bot_reply: str, action: dict | None = None) -> None:
        """Lưu phiên đàm thoại vào bảng chat_sessions."""
        try:
            user_entry = ChatSession(
                user_id=user_id,
                room_id=room_id,
                role="user",
                content=user_msg,
            )
            bot_entry = ChatSession(
                user_id=user_id,
                room_id=room_id,
                role="model",
                content=bot_reply,
                function_calls_json=json.dumps(action) if action else None,
            )
            db.session.add_all([user_entry, bot_entry])
            db.session.commit()
        except Exception as e:
            logger.warning(f"Failed to log chat session: {e}")
            db.session.rollback()

    @classmethod
    def handle_message(
        cls,
        user_id: int,
        message: str,
        room_id: int | None = None,
    ) -> dict[str, Any]:
        """
        Xử lý tin nhắn của cư dân, nhận diện intent và trả về câu trả lời tự nhiên kèm action cards.

        Args:
            user_id: ID khách thuê.
            message: Tin nhắn khách gửi.
            room_id: ID phòng (nếu đã xác định).
        """
        clean_msg = message.strip()
        msg_lower = clean_msg.lower()

        # 1. Tìm phòng của khách thuê nếu chưa truyền
        target_room = None
        if room_id:
            target_room = db.session.get(Room, room_id)
        else:
            # Tra cứu qua hợp đồng còn hiệu lực
            contract = (
                db.session.query(Contract)
                .filter(Contract.tenant_id == user_id, Contract.status == "active")
                .first()
            )
            if contract:
                target_room = contract.room
            else:
                # Thử tìm phòng có tenant_id
                target_room = db.session.query(Room).filter(Room.current_tenant_id == user_id).first()

        target_room_id = target_room.id if target_room else None

        # 2. Phân tích Intent & Function Calling
        # Intent A: Tra cứu Hóa đơn / Tiền phòng / Tiền điện / Tiền nước
        invoice_keywords = [
            "hóa đơn", "hoa don", "tiền phòng", "tien phong", "tiền điện", "tien dien",
            "tiền nước", "tien nuoc", "chuyển khoản", "thanh toán", "vietqr", "qr"
        ]
        if any(kw in msg_lower for kw in invoice_keywords) and target_room:
            # Lấy hóa đơn mới nhất của phòng
            latest_invoice = (
                db.session.query(Invoice)
                .filter(Invoice.room_id == target_room.id)
                .order_by(Invoice.year.desc(), Invoice.month.desc(), Invoice.id.desc())
                .first()
            )

            if latest_invoice:
                vietqr_url = VietQRService.generate_vietqr_image_url(
                    amount=latest_invoice.total_amount,
                    message=latest_invoice.payment_ref or f"SAMS P{target_room.room_number} T{latest_invoice.month}",
                )

                # Liệt kê tóm tắt các khoản
                item_details = []
                for it in latest_invoice.items:
                    item_details.append(f"• {it.description}: {int(it.subtotal):,}đ")
                breakdown = "\n".join(item_details) if item_details else ""

                status_vn = {
                    "unpaid": "Chưa thanh toán",
                    "paid": "Đã thanh toán",
                    "pending_verification": "Đang chờ đối soát biên lai",
                    "overdue": "Quá hạn thanh toán",
                }.get(latest_invoice.status, latest_invoice.status)

                reply_text = (
                    f"Dạ chào bạn! Hóa đơn tháng {latest_invoice.month}/{latest_invoice.year} của phòng {target_room.room_number}:\n"
                    f"- Tổng cộng: {int(latest_invoice.total_amount):,} VNĐ\n"
                    f"- Trạng thái: {status_vn}\n"
                )
                if breakdown:
                    reply_text += f"\nChi tiết các khoản mục:\n{breakdown}\n"

                if latest_invoice.status != "paid":
                    reply_text += "\nBạn có thể quét mã VietQR bên dưới để thanh toán nhanh 1-chạm hoặc tải biên lai chuyển khoản lên nhé!"

                attached_action = {
                    "type": "VIETQR_PAYMENT_CARD",
                    "invoice_id": latest_invoice.id,
                    "amount": float(latest_invoice.total_amount),
                    "status": latest_invoice.status,
                    "vietqr_url": vietqr_url,
                    "payment_ref": latest_invoice.payment_ref,
                }

                cls._log_chat(user_id, target_room_id, clean_msg, reply_text, attached_action)

                return {
                    "reply": reply_text,
                    "function_called": "get_unpaid_invoices",
                    "attached_action": attached_action,
                }

        # Intent B: Tra cứu Nội quy tòa nhà
        rule_keywords = [
            "nội quy", "noi quy", "giờ giấc", "gio giac", "khóa cổng", "khoa cong",
            "hút thuốc", "hut thuoc", "karaoke", "tiếng ồn", "ồn ào", "ở ghép", "bạn ở cùng", "tạm trú"
        ]
        if any(kw in msg_lower for kw in rule_keywords):
            reply_text = (
                "Dạ vâng, dưới đây là quy định chính của tòa nhà căn hộ SAMS:\n\n"
                "1. Giờ khóa cổng: 23:00 hàng ngày (dùng vân tay/thẻ từ).\n"
                "2. Giữ yên lặng: Sau 22:00 nghiêm cấm tiệc tùng, hát karaoke gây ồn.\n"
                "3. Rác thải: Để đúng nơi quy định trước 8:00 sáng, không để ngoài hành lang.\n"
                "4. An toàn: Cấm hút thuốc khu vực chung và thang máy. Sạc xe điện đúng vị trí quy định.\n"
                "5. Khách ngủ qua đêm: Cần đăng ký trước 21:00 để làm thủ tục tạm trú.\n\n"
                "Bạn cần hỗ trợ thêm thông tin chi tiết nào không ạ?"
            )
            cls._log_chat(user_id, target_room_id, clean_msg, reply_text)

            return {
                "reply": reply_text,
                "function_called": "get_building_rules",
                "attached_action": None,
            }

        # Intent C: Báo hỏng / Sự cố kỹ thuật
        ticket_keywords = ["hỏng", "hong", "sửa", "sua", "hư", "hu", "chập điện", "mất nước", "mat nuoc", "nghẹt", "bảo trì"]
        if any(kw in msg_lower for kw in ticket_keywords):
            reply_text = (
                "Dạ, mình đã ghi nhận thông tin sự cố kỹ thuật của bạn. "
                "Ban quản lý tòa nhà và đội ngũ kỹ thuật sẽ sắp xếp kiểm tra xử lý sớm nhất. "
                "Bạn có thể vào mục 'Yêu cầu sửa chữa' để đính kèm ảnh chụp hiện trạng hỏng hóc giúp kỹ thuật viên chuẩn bị dụng cụ phù hợp nhé!"
            )
            action = {
                "type": "OPEN_TICKET_FORM",
                "room_id": target_room_id,
            }
            cls._log_chat(user_id, target_room_id, clean_msg, reply_text, action)

            return {
                "reply": reply_text,
                "function_called": "report_service_ticket",
                "attached_action": action,
            }

        # Intent D: Bảng tin thông báo
        bulletin_keywords = ["thông báo", "thong bao", "bảng tin", "bang tin", "cắt nước", "cat nuoc", "cắt điện", "cat dien"]
        if any(kw in msg_lower for kw in bulletin_keywords):
            announcements = (
                db.session.query(BulletinAnnouncement)
                .order_by(BulletinAnnouncement.created_at.desc())
                .limit(3)
                .all()
            )
            if announcements:
                ann_texts = []
                for a in announcements:
                    ann_texts.append(f"• [{a.priority.upper()}] {a.title}: {a.content[:150]}...")
                reply_text = "Các thông báo mới nhất từ Ban quản lý tòa nhà:\n\n" + "\n\n".join(ann_texts)
            else:
                reply_text = "Hiện tại tòa nhà không có thông báo cắt điện, cắt nước hay sự cố khẩn cấp nào."

            cls._log_chat(user_id, target_room_id, clean_msg, reply_text)

            return {
                "reply": reply_text,
                "function_called": "get_bulletin_announcements",
                "attached_action": None,
            }

        # Fallback Gemini Generative AI (nếu có API Key)
        api_key = current_app.config.get("GEMINI_API_KEY", "") or os.environ.get("GEMINI_API_KEY", "")
        if api_key and not api_key.startswith("AIzaSyYour"):
            try:
                import google.generativeai as genai

                genai.configure(api_key=api_key)
                model_name = current_app.config.get("GEMINI_TEXT_MODEL", "gemini-1.5-flash")
                model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=f"Bạn là Trợ lý ảo AI thông minh và thân thiện của Tòa nhà Căn hộ SAMS. Nhiệm vụ của bạn là hỗ trợ cư dân giải đáp thắc mắc, hỏi tiền phòng, nhắc nhở thanh toán hóa đơn và hướng dẫn tuân thủ nội quy chung.\n{BUILDING_RULES}",
                )
                response = model.generate_content(clean_msg)
                if response and response.text:
                    gen_reply = response.text.strip()
                    cls._log_chat(user_id, target_room_id, clean_msg, gen_reply)
                    return {
                        "reply": gen_reply,
                        "function_called": None,
                        "attached_action": None,
                    }
            except Exception as e:
                logger.warning(f"Gemini Chat call failed: {e}")

        # Default Helpful Reply
        default_reply = (
            "Xin chào bạn! Mình là Trợ lý AI của căn hộ SAMS. "
            "Bạn có thể hỏi mình về: Hóa đơn & tiền điện nước tháng này, quy định giờ giấc & nội quy tòa nhà, hoặc thông báo bảng tin nhé!"
        )
        cls._log_chat(user_id, target_room_id, clean_msg, default_reply)

        return {
            "reply": default_reply,
            "function_called": None,
            "attached_action": None,
        }
