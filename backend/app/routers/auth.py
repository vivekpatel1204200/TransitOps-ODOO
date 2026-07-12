from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.models import User, Driver, RoleEnum
from app.models.schemas import UserCreate, LoginRequest, Token, UserOut
from app.services.notify_service import notify

router = APIRouter(prefix="/auth", tags=["auth"])

VALID_ROLES = {r.value for r in RoleEnum}


@router.post("/signup", response_model=UserOut)
def signup(payload: UserCreate, db: Session = Depends(get_db)):
    """Real registration — every signup is stored as a genuine row in Postgres
    (hashed password, real email), no demo/mock users involved."""
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    if payload.role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"role must be one of {sorted(VALID_ROLES)}")

    driver_id = None
    if payload.role == "driver" and payload.driver_id:
        driver = db.query(Driver).filter(Driver.id == payload.driver_id).first()
        if not driver:
            raise HTTPException(status_code=404, detail="Linked driver record not found")
        already_linked = db.query(User).filter(User.driver_id == payload.driver_id).first()
        if already_linked:
            raise HTTPException(status_code=400, detail="That driver profile is already linked to an account")
        driver_id = driver.id

    user = User(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        hashed_password=hash_password(payload.password),
        role=payload.role,
        driver_id=driver_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    notify(
        db, "user_registered", "New team member joined",
        f"{user.name} ({user.role.value if hasattr(user.role, 'value') else user.role}) just signed up.",
        severity="info", audience_role="fleet_manager",
    )
    return user


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    user.last_login = datetime.utcnow()
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.email, "role": user.role.value if hasattr(user.role, "value") else user.role})
    return Token(access_token=token, user=user)


@router.get("/available-drivers")
def available_drivers_for_linking(db: Session = Depends(get_db)):
    """Drivers who don't yet have a login account linked — used by the signup form
    so a real driver can pick their own operational profile when registering."""
    linked_ids = {u.driver_id for u in db.query(User).filter(User.driver_id.isnot(None)).all()}
    drivers = db.query(Driver).all()
    return [
        {"id": d.id, "name": d.name, "license_number": d.license_number}
        for d in drivers if d.id not in linked_ids
    ]
