from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


# ---------- Auth ----------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str
    phone: Optional[str] = None
    driver_id: Optional[str] = None  # only meaningful when role == "driver"


class UserOut(BaseModel):
    id: str
    name: str
    email: str
    role: str
    phone: Optional[str] = None
    driver_id: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Vehicle ----------
class VehicleCreate(BaseModel):
    registration_number: str
    name_model: str
    type: str
    max_load_capacity_kg: float
    odometer_km: float = 0
    acquisition_cost: float
    region: str = "Gujarat"


class VehicleOut(VehicleCreate):
    id: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Driver ----------
class DriverCreate(BaseModel):
    name: str
    license_number: str
    license_category: str
    license_expiry_date: datetime
    contact_number: str
    safety_score: float = 100.0


class DriverOut(DriverCreate):
    id: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Trip ----------
class TripCreate(BaseModel):
    source: str
    destination: str
    vehicle_id: str
    driver_id: str
    cargo_weight_kg: float
    planned_distance_km: float
    revenue: float = 0


class TripComplete(BaseModel):
    actual_distance_km: float
    fuel_consumed_l: float


class TripOut(BaseModel):
    id: str
    source: str
    destination: str
    vehicle_id: str
    driver_id: str
    cargo_weight_kg: float
    planned_distance_km: float
    actual_distance_km: Optional[float]
    fuel_consumed_l: Optional[float]
    revenue: float
    status: str
    dispatched_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Maintenance ----------
class MaintenanceCreate(BaseModel):
    vehicle_id: str
    description: str
    cost: float


class MaintenanceOut(MaintenanceCreate):
    id: str
    is_active: bool
    created_at: datetime
    closed_at: Optional[datetime]

    class Config:
        from_attributes = True


# ---------- Fuel ----------
class FuelCreate(BaseModel):
    vehicle_id: str
    liters: float
    cost: float


class FuelOut(FuelCreate):
    id: str
    date: datetime
    is_anomaly: bool

    class Config:
        from_attributes = True


# ---------- Expense ----------
class ExpenseCreate(BaseModel):
    vehicle_id: Optional[str] = None
    category: str
    amount: float
    notes: Optional[str] = None


class ExpenseOut(ExpenseCreate):
    id: str
    date: datetime

    class Config:
        from_attributes = True
