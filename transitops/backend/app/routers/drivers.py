from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Driver, DriverStatus
from app.models.schemas import DriverCreate, DriverOut

router = APIRouter(prefix="/drivers", tags=["drivers"])


@router.get("", response_model=list[DriverOut])
def list_drivers(
    status: Optional[str] = None,
    dispatch_pool_only: bool = False,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    q = db.query(Driver)
    if status:
        q = q.filter(Driver.status == status)
    if dispatch_pool_only:
        # Expired license or Suspended cannot be assigned
        q = q.filter(
            Driver.status == DriverStatus.available,
            Driver.license_expiry_date > datetime.utcnow(),
        )
    return q.order_by(Driver.created_at.desc()).all()


@router.post("", response_model=DriverOut)
def create_driver(payload: DriverCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    existing = db.query(Driver).filter(Driver.license_number == payload.license_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="License number already exists")
    driver = Driver(**payload.model_dump())
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return driver


@router.get("/{driver_id}", response_model=DriverOut)
def get_driver(driver_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver
