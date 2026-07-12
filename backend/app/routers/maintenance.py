from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import MaintenanceLog, Vehicle, VehicleStatus
from app.models.schemas import MaintenanceCreate, MaintenanceOut
from app.services.notify_service import notify

router = APIRouter(prefix="/maintenance", tags=["maintenance"])


@router.get("", response_model=list[MaintenanceOut])
def list_maintenance(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(MaintenanceLog).order_by(MaintenanceLog.created_at.desc()).all()


@router.post("", response_model=MaintenanceOut)
def create_maintenance(payload: MaintenanceCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    vehicle = db.query(Vehicle).filter(Vehicle.id == payload.vehicle_id).with_for_update().first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if vehicle.status == VehicleStatus.on_trip:
        raise HTTPException(status_code=400, detail="Cannot send an on-trip vehicle to maintenance")

    log = MaintenanceLog(**payload.model_dump(), is_active=True)
    db.add(log)
    # Business rule: creating active maintenance auto flips vehicle to In Shop
    vehicle.status = VehicleStatus.in_shop
    db.commit()
    db.refresh(log)

    notify(
        db, "maintenance_alert", "Vehicle sent to shop",
        f"{vehicle.registration_number} is now In Shop — {log.description} (₹{log.cost}).",
        severity="warning", data={"vehicle_id": vehicle.id, "log_id": log.id},
    )
    return log


@router.patch("/{log_id}/close", response_model=MaintenanceOut)
def close_maintenance(log_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    log = db.query(MaintenanceLog).filter(MaintenanceLog.id == log_id).with_for_update().first()
    if not log:
        raise HTTPException(status_code=404, detail="Maintenance log not found")
    if not log.is_active:
        raise HTTPException(status_code=400, detail="Already closed")

    vehicle = db.query(Vehicle).filter(Vehicle.id == log.vehicle_id).with_for_update().first()

    log.is_active = False
    log.closed_at = datetime.utcnow()

    # Restore to Available unless retired
    if vehicle.status != VehicleStatus.retired:
        vehicle.status = VehicleStatus.available

    db.commit()
    db.refresh(log)

    notify(
        db, "maintenance_closed", "Vehicle back in service",
        f"{vehicle.registration_number} maintenance closed and is available again.",
        severity="info", data={"vehicle_id": vehicle.id, "log_id": log.id},
    )
    return log
