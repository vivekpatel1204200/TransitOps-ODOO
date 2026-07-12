from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from jose import jwt, JWTError

from app.core.database import SessionLocal
from app.core.security import JWT_SECRET, ALGORITHM
from app.core.ws_manager import manager
from app.models.models import User

router = APIRouter()


def _resolve_role_from_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        email = payload.get("sub")
    except JWTError:
        return None
    if not email:
        return None
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        return user.role.value if user else None
    finally:
        db.close()


@router.websocket("/ws/events")
async def events_socket(websocket: WebSocket, token: str = Query(default="")):
    """
    Live notification stream for dashboards: new trips dispatched/completed,
    maintenance alerts, fuel anomalies, license expiry warnings, etc.
    Connect with: ws://.../ws/events?token=<JWT access token>
    """
    role = _resolve_role_from_token(token) if token else None
    if role is None:
        role = "guest"

    await manager.connect(websocket, role)
    try:
        await websocket.send_json({"type": "connected", "title": "Live feed connected",
                                    "message": "You'll now see real-time fleet updates.",
                                    "severity": "info", "data": {}, "timestamp": None})
        while True:
            # We don't need anything from the client; just keep the socket alive.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
