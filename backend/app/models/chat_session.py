"""
SAMS - ChatSession Model
Bảng chat_sessions: Lưu lịch sử hội thoại với Trợ lý ảo Gemini.
"""
from datetime import datetime, timezone
import json
from app.extensions import db


class ChatSession(db.Model):
    """
    Lịch sử tin nhắn đàm thoại giữa khách thuê và Gemini AI.
    Mỗi bản ghi là một tin nhắn (user hoặc model).
    role: 'user' | 'model'
    """
    __tablename__ = "chat_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    room_id = db.Column(
        db.Integer,
        db.ForeignKey("rooms.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    # 'user' = tin nhắn từ khách thuê, 'model' = phản hồi từ Gemini AI
    role = db.Column(db.String(10), nullable=False)
    content = db.Column(db.Text, nullable=False)
    # Lưu function_calls dạng JSON nếu Gemini thực hiện Function Calling
    function_calls_json = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def to_dict(self) -> dict:
        function_calls = None
        if self.function_calls_json:
            try:
                function_calls = json.loads(self.function_calls_json)
            except (json.JSONDecodeError, TypeError):
                function_calls = None
        return {
            "id": self.id,
            "user_id": self.user_id,
            "room_id": self.room_id,
            "role": self.role,
            "content": self.content,
            "function_calls": function_calls,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<ChatSession id={self.id} user={self.user_id} role={self.role}>"
