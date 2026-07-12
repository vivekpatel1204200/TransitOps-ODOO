"""
Run this AFTER the backend container is up:
    docker exec -it transitops_backend python seed.py
"""
import random
from datetime import datetime, timedelta

from faker import Faker

from app.core.database import SessionLocal, Base, engine
from app.core.security import hash_password
from app.models.models import (
    User, Vehicle, Driver, Trip, MaintenanceLog, FuelLog,
    VehicleStatus, DriverStatus, TripStatus,
)

fake = Faker("en_IN")
Base.metadata.create_all(bind=engine)
db = SessionLocal()

GJ_CITIES = ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Gandhinagar", "Bhavnagar"]
VEHICLE_TYPES = ["Mini-Truck", "Truck", "Van", "Container Truck"]
RTO_CODES = ["GJ-01", "GJ-05", "GJ-18", "GJ-27", "GJ-06"]


def reg_number():
    code = random.choice(RTO_CODES)
    return f"{code}-{random.choice('ABCDEFGH')}{random.choice('XYZ')}-{random.randint(1000,9999)}"


def seed_users():
    users = [
        ("Ravi Patel", "manager@transitops.in", "fleet_manager"),
        ("Priya Shah", "driver@transitops.in", "driver"),
        ("Amit Mehta", "safety@transitops.in", "safety_officer"),
        ("Neha Joshi", "finance@transitops.in", "financial_analyst"),
    ]
    for name, email, role in users:
        if not db.query(User).filter(User.email == email).first():
            db.add(User(name=name, email=email, hashed_password=hash_password("password123"), role=role))
    db.commit()
    print("Seeded users. Login with any of the above emails, password123")


def seed_vehicles(n=15):
    vehicles = []
    for _ in range(n):
        v = Vehicle(
            registration_number=reg_number(),
            name_model=random.choice(["Tata Ace", "Ashok Leyland Dost", "Mahindra Bolero Pickup", "Eicher Pro 2049", "Tata 407"]),
            type=random.choice(VEHICLE_TYPES),
            max_load_capacity_kg=random.choice([500, 750, 1000, 1500, 3000]),
            odometer_km=round(random.uniform(1000, 150000), 1),
            acquisition_cost=round(random.uniform(400000, 2500000), 2),
            status=random.choices(
                [VehicleStatus.available, VehicleStatus.on_trip, VehicleStatus.in_shop],
                weights=[0.6, 0.25, 0.15],
            )[0],
            region=random.choice(GJ_CITIES),
        )
        db.add(v)
        vehicles.append(v)
    db.commit()
    print(f"Seeded {n} vehicles.")
    return vehicles


def seed_drivers(n=12):
    drivers = []
    for _ in range(n):
        expiry = datetime.utcnow() + timedelta(days=random.randint(-30, 500))
        d = Driver(
            name=fake.name(),
            license_number=f"GJ{random.randint(10,99)}{random.randint(100000,999999)}",
            license_category=random.choice(["LMV", "HMV", "LMV-TR"]),
            license_expiry_date=expiry,
            contact_number=fake.phone_number(),
            safety_score=round(random.uniform(60, 100), 1),
            status=random.choices(
                [DriverStatus.available, DriverStatus.on_trip, DriverStatus.off_duty],
                weights=[0.6, 0.25, 0.15],
            )[0],
        )
        db.add(d)
        drivers.append(d)
    db.commit()
    print(f"Seeded {n} drivers.")
    return drivers


def seed_trips_maintenance_fuel(vehicles, drivers, n_trips=25):
    available_vehicles = [v for v in vehicles if v.status != VehicleStatus.in_shop]
    for _ in range(n_trips):
        vehicle = random.choice(available_vehicles)
        driver = random.choice(drivers)
        distance = round(random.uniform(50, 800), 1)
        status = random.choice([TripStatus.completed, TripStatus.completed, TripStatus.draft, TripStatus.cancelled])
        trip = Trip(
            source=random.choice(GJ_CITIES),
            destination=random.choice(GJ_CITIES),
            vehicle_id=vehicle.id,
            driver_id=driver.id,
            cargo_weight_kg=round(random.uniform(100, vehicle.max_load_capacity_kg), 1),
            planned_distance_km=distance,
            actual_distance_km=distance + random.uniform(-10, 10) if status == TripStatus.completed else None,
            fuel_consumed_l=round(distance / random.uniform(8, 14), 1) if status == TripStatus.completed else None,
            revenue=round(distance * random.uniform(35, 60), 2) if status == TripStatus.completed else 0,
            status=status,
        )
        db.add(trip)

    # Maintenance logs
    for v in random.sample(vehicles, k=min(6, len(vehicles))):
        db.add(MaintenanceLog(
            vehicle_id=v.id,
            description=random.choice(["Oil Change", "Tire Replacement", "Brake Service", "Engine Checkup"]),
            cost=round(random.uniform(1500, 25000), 2),
            is_active=(v.status == VehicleStatus.in_shop),
        ))

    # Fuel logs (mostly normal, a couple of anomalies for demo)
    for v in vehicles:
        for _ in range(random.randint(2, 5)):
            liters = round(random.uniform(20, 80), 1)
            rate = random.uniform(90, 105)  # normal diesel rate range INR/L
            db.add(FuelLog(vehicle_id=v.id, liters=liters, cost=round(liters * rate, 2)))
        # inject one anomaly
        if random.random() < 0.3:
            liters = round(random.uniform(20, 40), 1)
            db.add(FuelLog(vehicle_id=v.id, liters=liters, cost=round(liters * 300, 2), is_anomaly=True))

    db.commit()
    print(f"Seeded {n_trips} trips + maintenance + fuel logs.")


if __name__ == "__main__":
    seed_users()
    vehicles = seed_vehicles()
    drivers = seed_drivers()
    seed_trips_maintenance_fuel(vehicles, drivers)
    print("\n✅ Seeding complete. Backend has rich demo data now.")
