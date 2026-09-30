"""
SAMS - Gemini AI Chat Controller
Endpoint tương tác đàm thoại thời gian thực với Trợ lý ảo AI tòa nhà.
Tuân thủ API.md Section 3.7 và FR-AI-01, FR-AI-02.
"""
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity

from app.utils.response import success_response, error_response
from app.utils.decorators import authenticated_required
from app.services.gemini_chat_service import GeminiChatService

chat_bp = Blueprint("chat", __name__, url_prefix="/api/v1/chat")


@chat_bp.post("/message")
@authenticated_required
def send_chat_message():
    """
    Gửi tin nhắn đàm thoại tự nhiên tới Trợ lý ảo Gemini.
    AI tự động gọi Function Calling khi hỏi tiền phòng, tra cứu nội quy, hoặc báo hỏng.
    JSON Body:
        message: string
        room_id: integer (tùy chọn)
    """
    payload = request.get_json(silent=True) or {}
    message = payload.get("message")
    room_id = payload.get("room_id")

    if not message or not message.strip():
        return error_response("EMPTY_MESSAGE", "Nội dung tin nhắn không được để trống.", 400)

    user_id = int(get_jwt_identity())

    try:
        response_data = GeminiChatService.handle_message(
            user_id=user_id,
            message=message.strip(),
            room_id=int(room_id) if room_id else None,
        )
    except Exception as e:
        return error_response("AI_SERVICE_ERROR", f"Lỗi trợ lý AI: {str(e)}", 500)

    return success_response(data=response_data)
