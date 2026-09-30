"""
SAMS - Bulletin Announcements Controller
Bảng tin tòa nhà: thông báo bảo trì, cắt điện nước, an ninh.
"""
from datetime import datetime, timezone
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models.expense import BulletinAnnouncement
from app.utils.response import success_response, error_response
from app.utils.decorators import authenticated_required, landlord_required

announcements_bp = Blueprint("announcements", __name__, url_prefix="/api/v1/announcements")


@announcements_bp.get("")
@authenticated_required
def get_announcements():
    """Xem danh sách các thông báo trên bảng tin tòa nhà."""
    building_id = request.args.get("building_id", type=int)
    query = db.session.query(BulletinAnnouncement)
    if building_id:
        query = query.filter(BulletinAnnouncement.building_id == building_id)

    announcements = (
        query.order_by(
            BulletinAnnouncement.priority.desc(),
            BulletinAnnouncement.created_at.desc(),
        )
        .limit(50)
        .all()
    )
    return success_response(data=[a.to_dict() for a in announcements])


@announcements_bp.post("")
@landlord_required
def create_announcement():
    """Chủ nhà đăng thông báo mới lên bảng tin."""
    user_id = int(get_jwt_identity())
    payload = request.get_json(silent=True) or {}

    title = payload.get("title")
    content = payload.get("content")
    building_id = payload.get("building_id")
    priority = payload.get("priority", "normal")

    if not title or not content or not building_id:
        return error_response("MISSING_FIELDS", "title, content, building_id là bắt buộc.", 400)

    announcement = BulletinAnnouncement(
        building_id=int(building_id),
        author_id=user_id,
        title=title.strip(),
        content=content.strip(),
        priority=priority,
    )
    db.session.add(announcement)
    db.session.commit()

    return success_response(data=announcement.to_dict(), status_code=201)
