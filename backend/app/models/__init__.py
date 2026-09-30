"""
SAMS - Models Package
Import tất cả models để SQLAlchemy biết các bảng cần tạo.
Thứ tự import quan trọng vì các model có quan hệ FK với nhau.
"""
# Import theo thứ tự: base entities trước, dependent entities sau
from app.models.user import User
from app.models.room import Building, Room
from app.models.contract import Contract
from app.models.roommate import Roommate
from app.models.room_asset import RoomAsset
from app.models.invoice import Invoice, InvoiceItem
from app.models.utility_reading import UtilityReading
from app.models.violation import RoomViolation
from app.models.expense import Expense, BulletinAnnouncement, ServiceTicket
from app.models.chat_session import ChatSession
from app.models.otp import OtpVerification

__all__ = [
    "User",
    "Building",
    "Room",
    "Contract",
    "Roommate",
    "RoomAsset",
    "Invoice",
    "InvoiceItem",
    "UtilityReading",
    "RoomViolation",
    "Expense",
    "BulletinAnnouncement",
    "ServiceTicket",
    "ChatSession",
    "OtpVerification",
]
