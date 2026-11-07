"""Everything the dashboard needs for one day, in a single request."""

from datetime import date

from fastapi import APIRouter
from sqlalchemy import select

from app.deps import CurrentUser, DbSession
from app.models import FoodEntry, MealType, WeightEntry
from app.schemas import DashboardRead
from app.services.nutrition import summarise_day

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

RECENT_WEIGHTS_LIMIT = 14


@router.get("", response_model=DashboardRead)
def get_dashboard(user: CurrentUser, db: DbSession, day: date | None = None):
    # The frontend always sends the user's local date. The fallback uses the
    # server's date, which is UTC inside Docker.
    day = day or date.today()

    entries = db.scalars(
        select(FoodEntry)
        .where(FoodEntry.user_id == user.id, FoodEntry.eaten_on == day)
        .order_by(FoodEntry.created_at, FoodEntry.id)
    ).all()

    recent_weights = db.scalars(
        select(WeightEntry)
        .where(WeightEntry.user_id == user.id, WeightEntry.measured_on <= day)
        .order_by(WeightEntry.measured_on.desc())
        .limit(RECENT_WEIGHTS_LIMIT)
    ).all()

    totals = summarise_day(entries)
    target = user.daily_calorie_target

    # A dict comprehension; Ruby: `MealType.to_h { |m| [m, entries.select { |e| e.meal == m }] }`
    meals = {meal: [e for e in entries if e.meal == meal] for meal in MealType}

    # Returning a plain dict is fine: FastAPI converts it using `response_model`.
    return {
        "day": day,
        "calorie_target": target,
        "calories_remaining": None if target is None else target - totals.calories,
        "totals": totals,
        "meals": meals,
        "weight_on_day": next((w for w in recent_weights if w.measured_on == day), None),
        "recent_weights": recent_weights,
    }
