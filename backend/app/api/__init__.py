"""SAMS API Blueprints Package."""
from app.api.auth import auth_bp
from app.api.rooms import rooms_bp
from app.api.roommates import roommates_bp
from app.api.meters import meters_bp
from app.api.quick_invoices import quick_invoices_bp
from app.api.billing import billing_bp
from app.api.violations import violations_bp
from app.api.chat import chat_bp
from app.api.announcements import announcements_bp
from app.api.tickets import tickets_bp
from app.api.expenses import expenses_bp
from app.api.contracts import contracts_bp

__all__ = [
    "auth_bp",
    "rooms_bp",
    "roommates_bp",
    "meters_bp",
    "quick_invoices_bp",
    "billing_bp",
    "violations_bp",
    "chat_bp",
    "announcements_bp",
    "tickets_bp",
    "expenses_bp",
    "contracts_bp",
]
