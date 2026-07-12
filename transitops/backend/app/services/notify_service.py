import json
from typing import Optional
from sqlalchemy.orm import Session

from app.models.models import Notification
from app.core.ws_manager import manager


def notify(db: Session, event_type: str, title: str, message: str,
           severity: str = "info", audience_role: Optional[str] = None,
           data: Optional[dict] = None):
    """Persist a notification row AND push it live over the websocket."""
    row = Notification(
        type=event_type,
        title=title,
        message=message,
        severity=severity,
        audience_role=audience_role,
        payload_json=json.dumps(data or {}),
    )
    db.add(row)
    db.commit()

    manager.broadcast(
        event_type=event_type,
        title=title,
        message=message,
        severity=severity,
        audience_role=audience_role,
        data=data or {},
    )
