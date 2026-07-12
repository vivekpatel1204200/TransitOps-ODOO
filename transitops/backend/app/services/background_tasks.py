import asyncio
from datetime import datetime, timedelta

from app.core.database import SessionLocal
from app.models.models import Driver, Notification
from app.services.notify_service import notify

CHECK_INTERVAL_SECONDS = 60 * 30  # every 30 minutes
LICENSE_WARNING_WINDOW_DAYS = 14


def _scan_expiring_licenses():
    db = SessionLocal()
    try:
        soon = datetime.utcnow() + timedelta(days=LICENSE_WARNING_WINDOW_DAYS)
        expiring = db.query(Driver).filter(
            Driver.license_expiry_date <= soon,
            Driver.license_expiry_date > datetime.utcnow(),
        ).all()

        for d in expiring:
            already = db.query(Notification).filter(
                Notification.type == "license_expiring",
                Notification.message.contains(d.license_number),
                Notification.created_at >= datetime.utcnow() - timedelta(hours=24),
            ).first()
            if already:
                continue
            days_left = (d.license_expiry_date - datetime.utcnow()).days
            notify(
                db, "license_expiring", "Driver license expiring soon",
                f"{d.name}'s license ({d.license_number}) expires in {days_left} day(s).",
                severity="warning", audience_role="safety_officer",
                data={"driver_id": d.id},
            )
    finally:
        db.close()


async def license_expiry_watcher():
    """Runs forever in the background alongside the FastAPI app."""
    while True:
        try:
            _scan_expiring_licenses()
        except Exception:
            pass
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)
