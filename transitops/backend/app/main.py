from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app.routers import auth, vehicles, drivers, trips, maintenance, fuel, expenses, analytics, predictive, tracking_ws

# Create tables if they don't exist yet (Alembic recommended for real migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TransitOps API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(vehicles.router)
app.include_router(drivers.router)
app.include_router(trips.router)
app.include_router(maintenance.router)
app.include_router(fuel.router)
app.include_router(expenses.router)
app.include_router(analytics.router)
app.include_router(predictive.router)
app.include_router(tracking_ws.router)


@app.get("/health")
def health():
    return {"status": "ok"}
