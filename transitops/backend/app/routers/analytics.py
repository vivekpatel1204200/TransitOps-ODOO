import csv
import io
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Vehicle, Driver, Trip, MaintenanceLog, FuelLog, VehicleStatus, DriverStatus, TripStatus

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
