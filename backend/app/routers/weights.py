"""Weight log. Entries are keyed by date: one weigh-in per day."""

from datetime import date

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import CurrentUser, DbSession
from app.models import WeightEntry
from app.schemas import WeightRead, WeightUpsert

router = APIRouter(prefix="/weights", tags=["weights"])


def find_weight(db: Session, user_id: int, measured_on: date) -> WeightEntry | None:
    # Rails: `current_user.weight_entries.find_by(measured_on: measured_on)`
    stmt = select(WeightEntry).where(
        WeightEntry.user_id == user_id, WeightEntry.measured_on == measured_on
    )
    return db.scalars(stmt).first()


@router.get("", response_model=list[WeightRead])
def list_weights(user: CurrentUser, db: DbSession, limit: int = Query(default=90, ge=1, le=1000)):
    # Rails: `current_user.weight_entries.order(measured_on: :desc).limit(limit)`
    stmt = (
        select(WeightEntry)
        .where(WeightEntry.user_id == user.id)
        .order_by(WeightEntry.measured_on.desc())
        .limit(limit)
    )
    return db.scalars(stmt).all()


# PUT /api/weights/2026-09-22 creates or replaces that day's entry. Sending the
# same request twice gives the same result (it's idempotent), so a retry or a
# double-click can't create duplicates.
@router.put("/{measured_on}", response_model=WeightRead)
def upsert_weight(measured_on: date, payload: WeightUpsert, user: CurrentUser, db: DbSession):
    # Rails: `find_or_initialize_by(measured_on:)` followed by `update!(...)`
    entry = find_weight(db, user.id, measured_on)
    if entry is None:
        entry = WeightEntry(user_id=user.id, measured_on=measured_on)
        db.add(entry)
    entry.weight_kg = payload.weight_kg
    entry.note = payload.note
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{measured_on}", status_code=204)
def delete_weight(measured_on: date, user: CurrentUser, db: DbSession) -> None:
    entry = find_weight(db, user.id, measured_on)
    if entry is None:
        raise HTTPException(status_code=404, detail="No weight logged for that date")
    db.delete(entry)
    db.commit()
