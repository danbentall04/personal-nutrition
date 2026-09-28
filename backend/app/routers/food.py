"""Food log. Rails equivalent: `resources :food_entries, only: [:index, :create, :destroy]`."""

from datetime import date

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.deps import CurrentUser, DbSession
from app.models import FoodEntry
from app.schemas import FoodEntryCreate, FoodEntryRead

router = APIRouter(prefix="/food-entries", tags=["food"])


# `day: date` isn't in the path, so FastAPI reads it from the query string
# (?day=2026-09-22), parses it into a date, and returns a 422 if it's invalid.
@router.get("", response_model=list[FoodEntryRead])
def list_food_entries(day: date, user: CurrentUser, db: DbSession):
    stmt = (
        select(FoodEntry)
        .where(FoodEntry.user_id == user.id, FoodEntry.eaten_on == day)
        .order_by(FoodEntry.created_at, FoodEntry.id)
    )
    return db.scalars(stmt).all()


@router.post("", response_model=FoodEntryRead, status_code=201)
def create_food_entry(payload: FoodEntryCreate, user: CurrentUser, db: DbSession):
    # `**payload.model_dump()` expands the dict into keyword arguments, like
    # `FoodEntry.new(food_entry_params.merge(user_id: current_user.id))`.
    entry = FoodEntry(user_id=user.id, **payload.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{entry_id}", status_code=204)
def delete_food_entry(entry_id: int, user: CurrentUser, db: DbSession) -> None:
    entry = db.get(FoodEntry, entry_id)  # Rails: FoodEntry.find_by(id: entry_id)
    if entry is None or entry.user_id != user.id:
        raise HTTPException(status_code=404, detail="Food entry not found")
    db.delete(entry)
    db.commit()
