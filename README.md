# TransitOps — Smart Transport Operations Platform

## Stack
- Backend: FastAPI + SQLAlchemy + PostgreSQL + JWT Auth
- Frontend: React (Vite) + Tailwind + React-Leaflet + Recharts
- Real-time: WebSocket live tracking
- AI: Z-score fuel anomaly detection + RandomForest predictive maintenance

## Run it (one command, needs Docker Desktop installed)

```bash
docker-compose up --build
```

- Backend: http://localhost:8000  (docs at /docs)
- Frontend: http://localhost:5173
- Postgres: localhost:5432 (user: transitops / pass: transitops123)

## Seed demo data (run once, after containers are up)

```bash
docker exec -it transitops_backend python seed.py
```

This creates 4 demo users (all password `password123`):
- manager@transitops.in (fleet_manager)
- driver@transitops.in (driver)
- safety@transitops.in (safety_officer)
- finance@transitops.in (financial_analyst)

Plus 15 vehicles, 12 drivers, 25 trips, maintenance + fuel logs with Indian (Gujarat) context data.

## What's implemented
- JWT auth + RBAC (`app/core/security.py`)
- Vehicle & Driver registry with uniqueness constraints
- Trip state machine (Draft → Dispatched → Completed / Cancelled) fully atomic via `with_for_update()` row locks (`app/services/trip_service.py`)
- All mandatory business rules: capacity check, expired license block, double-booking block, dispatch-pool filtering
- Maintenance log auto-flips vehicle to "In Shop" and back
- Fuel log Z-score anomaly detection (`app/routers/fuel.py`)
- Dashboard KPIs via SQL aggregation (`app/routers/analytics.py`)
- Vehicle ROI formula exactly as spec'd
- Smart Dispatch suggestion (lowest cost/km ranking)
- RandomForest predictive maintenance risk score (`app/routers/predictive.py`)
- WebSocket live map with simulated truck movement (`app/routers/tracking_ws.py`)
- CSV export
- Dark mode toggle (Tailwind class strategy)

## Team split (suggested)
- **Dev A**: `app/core/`, `app/routers/auth.py`, `app/services/trip_service.py`, business rule edge cases
- **Dev B**: `frontend/src/pages/*` — forms, tables, dashboard polish
- **Dev C**: `tracking_ws.py` + `LiveMap.jsx`, `analytics.py` + `Analytics.jsx`, predictive.py

## Next steps to extend
- Add Alembic migrations (`alembic init alembic`) instead of `Base.metadata.create_all`
- Add email reminder background task for expiring licenses (bonus feature)
- PDF export (bonus feature)
