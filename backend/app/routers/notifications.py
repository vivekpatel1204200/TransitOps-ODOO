from fastapi import APIRouter, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Notification, User

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("")
def list_notifications(limit: int = 20, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    role = user.role.value if hasattr(user.role, "value") else user.role
    q = db.query(Notification).filter(
        or_(Notification.audience_role.is_(None), Notification.audience_role == role, role == "fleet_manager")
    ).order_by(Notification.created_at.desc()).limit(limit)
    return [
        {
            "id": n.id,
            "type": n.type,
            "title": n.title,
            "message": n.message,
            "severity": n.severity,
            "created_at": n.created_at,
        }
        for n in q.all()
    ]
