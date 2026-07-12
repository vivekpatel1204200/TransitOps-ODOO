from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Trip
from app.models.schemas import TripCreate, TripOut, TripComplete
from app.services import trip_service

router = APIRouter(prefix="/trips", tags=["trips"])


@router.get("", response_model=list[TripOut])
def list_trips(status: Optional[str] = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    q = db.query(Trip)
    if status:
        q = q.filter(Trip.status == status)
    return q.order_by(Trip.created_at.desc()).all()


@router.post("", response_model=TripOut)
def create_trip(payload: TripCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return trip_service.create_trip(db, payload)


@router.post("/{trip_id}/dispatch", response_model=TripOut)
def dispatch_trip(trip_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return trip_service.dispatch_trip(db, trip_id)


@router.post("/{trip_id}/complete", response_model=TripOut)
def complete_trip(trip_id: str, payload: TripComplete, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return trip_service.complete_trip(db, trip_id, payload.actual_distance_km, payload.fuel_consumed_l)


@router.post("/{trip_id}/cancel", response_model=TripOut)
def cancel_trip(trip_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return trip_service.cancel_trip(db, trip_id)
