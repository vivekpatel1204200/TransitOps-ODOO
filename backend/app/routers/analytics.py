import csv
import io
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import (
    Vehicle, Driver, Trip, MaintenanceLog, FuelLog, Expense, User,
    VehicleStatus, DriverStatus, TripStatus,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard")
def dashboard_kpis(db: Session = Depends(get_db), user=Depends(get_current_user)):
    total_vehicles = db.query(func.count(Vehicle.id)).filter(Vehicle.status != VehicleStatus.retired).scalar()
    active_vehicles = db.query(func.count(Vehicle.id)).filter(Vehicle.status == VehicleStatus.on_trip).scalar()
    available_vehicles = db.query(func.count(Vehicle.id)).filter(Vehicle.status == VehicleStatus.available).scalar()
    in_maintenance = db.query(func.count(Vehicle.id)).filter(Vehicle.status == VehicleStatus.in_shop).scalar()

    active_trips = db.query(func.count(Trip.id)).filter(Trip.status == TripStatus.dispatched).scalar()
    pending_trips = db.query(func.count(Trip.id)).filter(Trip.status == TripStatus.draft).scalar()
    drivers_on_duty = db.query(func.count(Driver.id)).filter(Driver.status == DriverStatus.on_trip).scalar()

    fleet_utilization = round((active_vehicles / total_vehicles) * 100, 2) if total_vehicles else 0

    return {
        "active_vehicles": active_vehicles,
        "available_vehicles": available_vehicles,
        "vehicles_in_maintenance": in_maintenance,
        "active_trips": active_trips,
        "pending_trips": pending_trips,
        "drivers_on_duty": drivers_on_duty,
        "fleet_utilization_pct": fleet_utilization,
    }


@router.get("/vehicle-performance")
def vehicle_performance(db: Session = Depends(get_db), user=Depends(get_current_user)):
    vehicles = db.query(Vehicle).filter(Vehicle.status != VehicleStatus.retired).all()
    result = []

    for v in vehicles:
        total_distance = sum(t.actual_distance_km or 0 for t in v.trips if t.status == TripStatus.completed)
        total_fuel = sum(t.fuel_consumed_l or 0 for t in v.trips if t.status == TripStatus.completed)
        total_revenue = sum(t.revenue or 0 for t in v.trips if t.status == TripStatus.completed)
        maintenance_cost = sum(m.cost for m in v.maintenance_logs)
        fuel_cost = sum(f.cost for f in v.fuel_logs)
        operational_cost = maintenance_cost + fuel_cost

        fuel_efficiency = round(total_distance / total_fuel, 2) if total_fuel else 0
        roi = round((total_revenue - operational_cost) / v.acquisition_cost, 4) if v.acquisition_cost else 0

        result.append({
            "vehicle_id": v.id,
            "registration_number": v.registration_number,
            "fuel_efficiency_km_per_l": fuel_efficiency,
            "operational_cost": round(operational_cost, 2),
            "total_revenue": round(total_revenue, 2),
            "roi": roi,
        })

    return result


@router.get("/smart-dispatch")
def smart_dispatch_suggestions(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Rank available vehicles by lowest operational cost per km driven so far."""
    vehicles = db.query(Vehicle).filter(Vehicle.status == VehicleStatus.available).all()
    ranked = []
    for v in vehicles:
        total_distance = sum(t.actual_distance_km or 0 for t in v.trips if t.status == TripStatus.completed)
        maintenance_cost = sum(m.cost for m in v.maintenance_logs)
        fuel_cost = sum(f.cost for f in v.fuel_logs)
        cost_per_km = round((maintenance_cost + fuel_cost) / total_distance, 2) if total_distance else 0
        ranked.append({
            "vehicle_id": v.id,
            "registration_number": v.registration_number,
            "cost_per_km": cost_per_km,
        })
    ranked.sort(key=lambda x: x["cost_per_km"])
    return ranked


def _role_value(user: User) -> str:
    return user.role.value if hasattr(user.role, "value") else user.role


def _manager_dashboard(db: Session):
    return dashboard_kpis(db=db, user=None) | {
        "vehicle_performance": vehicle_performance(db=db, user=None)[:6],
        "recent_trips": [
            {
                "id": t.id, "source": t.source, "destination": t.destination,
                "status": t.status.value, "revenue": t.revenue,
            }
            for t in db.query(Trip).order_by(Trip.created_at.desc()).limit(8).all()
        ],
    }


def _driver_dashboard(db: Session, user: User):
    if not user.driver_id:
        return {"linked": False, "message": "Your account isn't linked to a driver profile yet."}

    driver = db.query(Driver).filter(Driver.id == user.driver_id).first()
    if not driver:
        return {"linked": False, "message": "Linked driver profile not found."}

    my_trips = db.query(Trip).filter(Trip.driver_id == driver.id).order_by(Trip.created_at.desc()).all()
    active_trip = next((t for t in my_trips if t.status == TripStatus.dispatched), None)
    completed = [t for t in my_trips if t.status == TripStatus.completed]
    days_to_expiry = (driver.license_expiry_date - datetime.utcnow()).days

    return {
        "linked": True,
        "driver_name": driver.name,
        "status": driver.status.value,
        "safety_score": driver.safety_score,
        "license_number": driver.license_number,
        "license_expiry_date": driver.license_expiry_date,
        "license_days_left": days_to_expiry,
        "license_expired": days_to_expiry < 0,
        "active_trip": {
            "id": active_trip.id, "source": active_trip.source, "destination": active_trip.destination,
            "dispatched_at": active_trip.dispatched_at,
        } if active_trip else None,
        "completed_trip_count": len(completed),
        "total_distance_km": round(sum(t.actual_distance_km or 0 for t in completed), 1),
        "recent_trips": [
            {"id": t.id, "source": t.source, "destination": t.destination, "status": t.status.value,
             "revenue": t.revenue, "actual_distance_km": t.actual_distance_km}
            for t in my_trips[:8]
        ],
    }


def _safety_dashboard(db: Session):
    now = datetime.utcnow()
    soon = now + timedelta(days=14)
    drivers = db.query(Driver).all()

    expiring_soon = [d for d in drivers if now < d.license_expiry_date <= soon]
    expired = [d for d in drivers if d.license_expiry_date <= now]
    low_safety = sorted([d for d in drivers if d.safety_score < 75], key=lambda d: d.safety_score)

    return {
        "total_drivers": len(drivers),
        "on_trip": len([d for d in drivers if d.status == DriverStatus.on_trip]),
        "suspended": len([d for d in drivers if d.status == DriverStatus.suspended]),
        "expired_licenses": [
            {"id": d.id, "name": d.name, "license_number": d.license_number,
             "license_expiry_date": d.license_expiry_date} for d in expired
        ],
        "expiring_soon": [
            {"id": d.id, "name": d.name, "license_number": d.license_number,
             "days_left": (d.license_expiry_date - now).days} for d in expiring_soon
        ],
        "low_safety_scores": [
            {"id": d.id, "name": d.name, "safety_score": d.safety_score} for d in low_safety[:8]
        ],
        "active_trips": db.query(func.count(Trip.id)).filter(Trip.status == TripStatus.dispatched).scalar(),
    }


def _finance_dashboard(db: Session):
    completed = db.query(Trip).filter(Trip.status == TripStatus.completed).all()
    total_revenue = sum(t.revenue or 0 for t in completed)
    total_maintenance_cost = sum(m.cost for m in db.query(MaintenanceLog).all())
    total_fuel_cost = sum(f.cost for f in db.query(FuelLog).all())
    total_expenses = sum(e.amount for e in db.query(Expense).all())
    anomalies = db.query(FuelLog).filter(FuelLog.is_anomaly == True).order_by(FuelLog.date.desc()).limit(5).all()  # noqa: E712

    operational_cost = total_maintenance_cost + total_fuel_cost + total_expenses
    net_margin = total_revenue - operational_cost

    return {
        "total_revenue": round(total_revenue, 2),
        "total_maintenance_cost": round(total_maintenance_cost, 2),
        "total_fuel_cost": round(total_fuel_cost, 2),
        "total_misc_expenses": round(total_expenses, 2),
        "operational_cost": round(operational_cost, 2),
        "net_margin": round(net_margin, 2),
        "completed_trip_count": len(completed),
        "roi_leaderboard": sorted(vehicle_performance(db=db, user=None), key=lambda x: -x["roi"])[:6],
        "recent_fuel_anomalies": [
            {"id": a.id, "vehicle_id": a.vehicle_id, "liters": a.liters, "cost": a.cost, "date": a.date}
            for a in anomalies
        ],
    }


@router.get("/dashboard/me")
def my_dashboard(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Returns a different payload shape depending on the logged-in user's role,
    so each role gets its own purpose-built dashboard."""
    role = _role_value(user)
    if role == "driver":
        return {"role": role, "data": _driver_dashboard(db, user)}
    if role == "safety_officer":
        return {"role": role, "data": _safety_dashboard(db)}
    if role == "financial_analyst":
        return {"role": role, "data": _finance_dashboard(db)}
    # fleet_manager (default / catch-all)
    return {"role": "fleet_manager", "data": _manager_dashboard(db)}


@router.get("/export/csv")
def export_csv(db: Session = Depends(get_db), user=Depends(get_current_user)):
    trips = db.query(Trip).all()
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "source", "destination", "vehicle_id", "driver_id", "status", "revenue", "actual_distance_km", "fuel_consumed_l"])
    for t in trips:
        writer.writerow([t.id, t.source, t.destination, t.vehicle_id, t.driver_id, t.status.value, t.revenue, t.actual_distance_km, t.fuel_consumed_l])
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=trips_export.csv"},
    )
