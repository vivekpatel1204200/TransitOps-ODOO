from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Vehicle, VehicleStatus
from app.models.schemas import VehicleCreate, VehicleOut

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get("", response_model=list[VehicleOut])
def list_vehicles(
    status: Optional[str] = None,
    type: Optional[str] = None,
    region: Optional[str] = None,
    dispatch_pool_only: bool = False,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    q = db.query(Vehicle)
    if status:
        q = q.filter(Vehicle.status == status)
    if type:
        q = q.filter(Vehicle.type == type)
    if region:
        q = q.filter(Vehicle.region == region)
    if dispatch_pool_only:
        # Retired / In Shop must never appear in dispatch selection
        q = q.filter(Vehicle.status == VehicleStatus.available)
    return q.order_by(Vehicle.created_at.desc()).all()


@router.post("", response_model=VehicleOut)
def create_vehicle(payload: VehicleCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    existing = db.query(Vehicle).filter(Vehicle.registration_number == payload.registration_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Registration number already exists")
    vehicle = Vehicle(**payload.model_dump())
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle


@router.get("/{vehicle_id}", response_model=VehicleOut)
def get_vehicle(vehicle_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


@router.patch("/{vehicle_id}/retire", response_model=VehicleOut)
def retire_vehicle(vehicle_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if vehicle.status == VehicleStatus.on_trip:
        raise HTTPException(status_code=400, detail="Cannot retire a vehicle that is on trip")
    vehicle.status = VehicleStatus.retired
    db.commit()
    db.refresh(vehicle)
    return vehicle
