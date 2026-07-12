from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.models import Trip, Vehicle, Driver, VehicleStatus, DriverStatus, TripStatus


def create_trip(db: Session, payload) -> Trip:
    vehicle = db.query(Vehicle).filter(Vehicle.id == payload.vehicle_id).with_for_update().first()
    driver = db.query(Driver).filter(Driver.id == payload.driver_id).with_for_update().first()

    if not vehicle or not driver:
        raise HTTPException(status_code=404, detail="Vehicle or driver not found")

    if vehicle.status != VehicleStatus.available:
        raise HTTPException(status_code=400, detail=f"Vehicle is {vehicle.status.value}, not Available")

    if driver.status != DriverStatus.available:
        raise HTTPException(status_code=400, detail=f"Driver is {driver.status.value}, not Available")

    if driver.license_expiry_date <= datetime.utcnow():
        raise HTTPException(status_code=400, detail="Driver license has expired")

    if payload.cargo_weight_kg > vehicle.max_load_capacity_kg:
        raise HTTPException(
            status_code=400,
            detail=f"Cargo weight {payload.cargo_weight_kg}kg exceeds vehicle capacity {vehicle.max_load_capacity_kg}kg",
        )

    trip = Trip(**payload.model_dump(), status=TripStatus.draft)
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


def dispatch_trip(db: Session, trip_id: str) -> Trip:
    trip = db.query(Trip).filter(Trip.id == trip_id).with_for_update().first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    if trip.status != TripStatus.draft:
        raise HTTPException(status_code=400, detail=f"Trip is {trip.status.value}, cannot dispatch")

    vehicle = db.query(Vehicle).filter(Vehicle.id == trip.vehicle_id).with_for_update().first()
    driver = db.query(Driver).filter(Driver.id == trip.driver_id).with_for_update().first()

    if vehicle.status != VehicleStatus.available:
        raise HTTPException(status_code=400, detail="Vehicle no longer available")
    if driver.status != DriverStatus.available:
        raise HTTPException(status_code=400, detail="Driver no longer available")

    # Atomic: flip both together
    trip.status = TripStatus.dispatched
    trip.dispatched_at = datetime.utcnow()
    vehicle.status = VehicleStatus.on_trip
    driver.status = DriverStatus.on_trip

    db.commit()
    db.refresh(trip)
    return trip


def complete_trip(db: Session, trip_id: str, actual_distance_km: float, fuel_consumed_l: float) -> Trip:
    trip = db.query(Trip).filter(Trip.id == trip_id).with_for_update().first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    if trip.status != TripStatus.dispatched:
        raise HTTPException(status_code=400, detail=f"Trip is {trip.status.value}, cannot complete")

    vehicle = db.query(Vehicle).filter(Vehicle.id == trip.vehicle_id).with_for_update().first()
    driver = db.query(Driver).filter(Driver.id == trip.driver_id).with_for_update().first()

    trip.status = TripStatus.completed
    trip.completed_at = datetime.utcnow()
    trip.actual_distance_km = actual_distance_km
    trip.fuel_consumed_l = fuel_consumed_l

    vehicle.odometer_km += actual_distance_km
    vehicle.status = VehicleStatus.available
    driver.status = DriverStatus.available

    db.commit()
    db.refresh(trip)
    return trip


def cancel_trip(db: Session, trip_id: str) -> Trip:
    trip = db.query(Trip).filter(Trip.id == trip_id).with_for_update().first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    if trip.status not in (TripStatus.draft, TripStatus.dispatched):
        raise HTTPException(status_code=400, detail=f"Trip is {trip.status.value}, cannot cancel")

    was_dispatched = trip.status == TripStatus.dispatched
    trip.status = TripStatus.cancelled

    if was_dispatched:
        vehicle = db.query(Vehicle).filter(Vehicle.id == trip.vehicle_id).with_for_update().first()
        driver = db.query(Driver).filter(Driver.id == trip.driver_id).with_for_update().first()
        vehicle.status = VehicleStatus.available
        driver.status = DriverStatus.available

    db.commit()
    db.refresh(trip)
    return trip
