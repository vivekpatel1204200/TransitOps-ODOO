import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Enum, Text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class RoleEnum(str, enum.Enum):
    fleet_manager = "fleet_manager"
    driver = "driver"
    safety_officer = "safety_officer"
    financial_analyst = "financial_analyst"


class VehicleStatus(str, enum.Enum):
    available = "Available"
    on_trip = "On Trip"
    in_shop = "In Shop"
    retired = "Retired"


class DriverStatus(str, enum.Enum):
    available = "Available"
    on_trip = "On Trip"
    off_duty = "Off Duty"
    suspended = "Suspended"


class TripStatus(str, enum.Enum):
    draft = "Draft"
    dispatched = "Dispatched"
    completed = "Completed"
    cancelled = "Cancelled"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    # Optional link from a "driver" role account to their operational Driver record,
    # so a real driver login can see their own trips/safety score.
    driver_id = Column(UUID(as_uuid=False), ForeignKey("drivers.id"), nullable=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    driver = relationship("Driver", foreign_keys=[driver_id])


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    registration_number = Column(String, unique=True, nullable=False, index=True)
    name_model = Column(String, nullable=False)
    type = Column(String, nullable=False)  # Truck, Van, Mini-Truck, etc
    max_load_capacity_kg = Column(Float, nullable=False)
    odometer_km = Column(Float, default=0)
    acquisition_cost = Column(Float, nullable=False)
    status = Column(Enum(VehicleStatus), default=VehicleStatus.available)
    region = Column(String, default="Gujarat")
    created_at = Column(DateTime, default=datetime.utcnow)

    trips = relationship("Trip", back_populates="vehicle")
    maintenance_logs = relationship("MaintenanceLog", back_populates="vehicle")
    fuel_logs = relationship("FuelLog", back_populates="vehicle")


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    license_number = Column(String, unique=True, nullable=False)
    license_category = Column(String, nullable=False)  # LMV, HMV, etc
    license_expiry_date = Column(DateTime, nullable=False)
    contact_number = Column(String, nullable=False)
    safety_score = Column(Float, default=100.0)
    status = Column(Enum(DriverStatus), default=DriverStatus.available)
    created_at = Column(DateTime, default=datetime.utcnow)

    trips = relationship("Trip", back_populates="driver")


class Trip(Base):
    __tablename__ = "trips"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    source = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    vehicle_id = Column(UUID(as_uuid=False), ForeignKey("vehicles.id"), nullable=False)
    driver_id = Column(UUID(as_uuid=False), ForeignKey("drivers.id"), nullable=False)
    cargo_weight_kg = Column(Float, nullable=False)
    planned_distance_km = Column(Float, nullable=False)
    actual_distance_km = Column(Float, nullable=True)
    fuel_consumed_l = Column(Float, nullable=True)
    revenue = Column(Float, default=0)
    status = Column(Enum(TripStatus), default=TripStatus.draft)
    dispatched_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    vehicle = relationship("Vehicle", back_populates="trips")
    driver = relationship("Driver", back_populates="trips")


class MaintenanceLog(Base):
    __tablename__ = "maintenance_logs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    vehicle_id = Column(UUID(as_uuid=False), ForeignKey("vehicles.id"), nullable=False)
    description = Column(String, nullable=False)  # Oil Change, Tire Replacement...
    cost = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)  # True = In Shop, False = Closed
    created_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)

    vehicle = relationship("Vehicle", back_populates="maintenance_logs")


class FuelLog(Base):
    __tablename__ = "fuel_logs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    vehicle_id = Column(UUID(as_uuid=False), ForeignKey("vehicles.id"), nullable=False)
    liters = Column(Float, nullable=False)
    cost = Column(Float, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    is_anomaly = Column(Boolean, default=False)  # flagged by z-score check

    vehicle = relationship("Vehicle", back_populates="fuel_logs")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    type = Column(String, nullable=False)  # trip_dispatched, trip_completed, maintenance_alert, fuel_anomaly, license_expiring
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    severity = Column(String, default="info")  # info, warning, critical
    audience_role = Column(String, nullable=True)  # None = everyone, else restrict to a role
    payload_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    vehicle_id = Column(UUID(as_uuid=False), ForeignKey("vehicles.id"), nullable=True)
    category = Column(String, nullable=False)  # Toll, Fine, Misc
    amount = Column(Float, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
