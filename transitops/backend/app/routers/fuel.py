import numpy as np
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import FuelLog
from app.models.schemas import FuelCreate, FuelOut

router = APIRouter(prefix="/fuel", tags=["fuel"])

Z_SCORE_THRESHOLD = 2.0  # flag anything beyond 2 std deviations as suspicious


@router.get("", response_model=list[FuelOut])
def list_fuel_logs(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(FuelLog).order_by(FuelLog.date.desc()).all()


@router.post("", response_model=FuelOut)
def create_fuel_log(payload: FuelCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # cost-per-liter based anomaly check against history for this vehicle
    history = db.query(FuelLog).filter(FuelLog.vehicle_id == payload.vehicle_id).all()
    rate = payload.cost / payload.liters if payload.liters else 0
    is_anomaly = False

    if len(history) >= 3:
        rates = [h.cost / h.liters for h in history if h.liters]
        mean = np.mean(rates)
        std = np.std(rates)
        if std > 0:
            z = abs((rate - mean) / std)
            is_anomaly = z > Z_SCORE_THRESHOLD

    log = FuelLog(**payload.model_dump(), is_anomaly=is_anomaly)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
