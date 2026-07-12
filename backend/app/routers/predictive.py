from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import numpy as np
from sklearn.ensemble import RandomForestRegressor

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Vehicle, TripStatus

router = APIRouter(prefix="/predictive-maintenance", tags=["predictive"])


@router.get("")
def predict_maintenance(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """
    Lightweight predictive maintenance model.
    Trains on synthetic feature relationship: odometer + trip count + maintenance history
    -> predicted 'risk score' (0-100) for needing maintenance soon.
    In a hackathon context we bootstrap with a rule-informed synthetic training set,
    then score real vehicles against it.
    """
    vehicles = db.query(Vehicle).filter(Vehicle.status != "Retired").all()
    if not vehicles:
        return []

    # Synthetic bootstrap training data: [odometer_km, completed_trips, maintenance_count] -> risk
    rng = np.random.default_rng(42)
    n = 300
    odo = rng.uniform(0, 200000, n)
    trips = rng.integers(0, 150, n)
    maint = rng.integers(0, 10, n)
    risk = np.clip((odo / 2500) + (trips * 0.4) + (maint * 8) + rng.normal(0, 5, n), 0, 100)

    X_train = np.column_stack([odo, trips, maint])
    model = RandomForestRegressor(n_estimators=60, max_depth=6, random_state=42)
    model.fit(X_train, risk)

    results = []
    for v in vehicles:
        completed_trips = len([t for t in v.trips if t.status == TripStatus.completed])
        maintenance_count = len(v.maintenance_logs)
        features = np.array([[v.odometer_km, completed_trips, maintenance_count]])
        score = float(model.predict(features)[0])
        results.append({
            "vehicle_id": v.id,
            "registration_number": v.registration_number,
            "risk_score": round(score, 1),
            "recommendation": "Schedule maintenance soon" if score > 65 else "Healthy",
        })

    results.sort(key=lambda x: -x["risk_score"])
    return results
