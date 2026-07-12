import asyncio
import json
from datetime import datetime
from typing import Optional

from fastapi import WebSocket


class ConnectionManager:
    """
    Tracks live /ws/events connections and lets normal (sync) request handlers
    push realtime events to every connected dashboard, filtered by role.

    FastAPI runs sync `def` route handlers in a worker thread, so we can't just
    `await` a broadcast from inside them. Instead we capture the running event
    loop at startup and use `run_coroutine_threadsafe` to hand the broadcast
    back to it safely from any thread.
    """

    def __init__(self):
        self.active: list[dict] = []  # [{"ws": WebSocket, "role": str}]
        self.loop: Optional[asyncio.AbstractEventLoop] = None

    def set_loop(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop

    async def connect(self, websocket: WebSocket, role: str):
        await websocket.accept()
        self.active.append({"ws": websocket, "role": role})

    def disconnect(self, websocket: WebSocket):
        self.active = [c for c in self.active if c["ws"] is not websocket]

    async def _broadcast_async(self, message: dict, audience_role: Optional[str]):
        dead = []
        for conn in list(self.active):
            if audience_role and conn["role"] != audience_role and conn["role"] != "fleet_manager":
                continue
            try:
                await conn["ws"].send_json(message)
            except Exception:
                dead.append(conn["ws"])
        for ws in dead:
            self.disconnect(ws)

    def broadcast(self, event_type: str, title: str, message: str, severity: str = "info",
                  audience_role: Optional[str] = None, data: Optional[dict] = None):
        """Call this from anywhere (sync or async) to push a live event to dashboards."""
        payload = {
            "type": event_type,
            "title": title,
            "message": message,
            "severity": severity,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat(),
        }
        if self.loop is None:
            return
        try:
            asyncio.run_coroutine_threadsafe(
                self._broadcast_async(payload, audience_role), self.loop
            )
        except RuntimeError:
            pass


manager = ConnectionManager()
