import asyncio
import random
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.models import Trip, TripStatus

router = APIRouter()

# Rough Gujarat bounding box for demo coordinate simulation
LAT_RANGE = (21.0, 24.5)
LNG_RANGE = (68.5, 74.5)


def get_dispatched_trips(db: Session):
    return db.query(Trip).filter(Trip.status == TripStatus.dispatched).all()


@router.websocket("/ws/tracking")
async def tracking_socket(websocket: WebSocket):
    await websocket.accept()
    # seed a starting point per trip for this connection session
    positions = {}
    try:
        while True:
            db = SessionLocal()
            trips = get_dispatched_trips(db)
            db.close()

            payload = []
            for t in trips:
                if t.id not in positions:
                    positions[t.id] = [
                        random.uniform(*LAT_RANGE),
                        random.uniform(*LNG_RANGE),
                    ]
                # small random walk to simulate movement
                positions[t.id][0] += random.uniform(-0.02, 0.02)
                positions[t.id][1] += random.uniform(-0.02, 0.02)

                payload.append({
                    "trip_id": t.id,
                    "vehicle_id": t.vehicle_id,
                    "lat": positions[t.id][0],
                    "lng": positions[t.id][1],
                    "source": t.source,
                    "destination": t.destination,
                })

            await websocket.send_json({"trips": payload})
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        pass
