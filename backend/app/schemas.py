"""Request and response shapes for the API (Pydantic models).

Rails equivalent: strong parameters (`params.require(:food_entry).permit(...)`)
plus a serializer/jbuilder view, in one place. FastAPI uses these classes to:
  - validate incoming JSON (bad input -> automatic 422 error with details)
  - decide exactly which fields go out in the response
  - generate the interactive docs at http://localhost:8000/docs

`...Read` classes describe responses; the others describe request bodies.
`from_attributes=True` lets Pydantic build a response straight from a
SQLAlchemy object (like `render json: @food_entry` in Rails).
"""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.models import Goal, MealType, Sex


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# --- Profile ---------------------------------------------------------------


class ProfileUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str | None = Field(default=None, max_length=255)
    date_of_birth: date | None = None
    sex: Sex | None = None
    height_cm: float | None = Field(default=None, gt=0, lt=300)
    goal: Goal = Goal.MAINTAIN
    target_weight_kg: float | None = Field(default=None, gt=0, lt=500)
    daily_calorie_target: int | None = Field(default=None, gt=0, lt=10000)
    dietary_notes: str | None = None


class ProfileRead(ProfileUpdate, ORMModel):
    id: int


# --- Weight ----------------------------------------------------------------


class WeightUpsert(BaseModel):
    weight_kg: float = Field(gt=0, lt=500)
    note: str | None = Field(default=None, max_length=500)


class WeightRead(ORMModel):
    id: int
    measured_on: date
    weight_kg: float
    note: str | None


# --- Food ------------------------------------------------------------------


class FoodEntryCreate(BaseModel):
    eaten_on: date
    meal: MealType
    name: str = Field(min_length=1, max_length=200)
    quantity: str | None = Field(default=None, max_length=100)
    calories: int = Field(ge=0, le=10000)
    protein_g: float | None = Field(default=None, ge=0, le=1000)
    carbs_g: float | None = Field(default=None, ge=0, le=1000)
    fat_g: float | None = Field(default=None, ge=0, le=1000)


class FoodEntryRead(FoodEntryCreate, ORMModel):
    id: int


# --- Dashboard -------------------------------------------------------------


class DayTotalsRead(ORMModel):
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    # How many entries had no macro data, so the UI can show that the macro
    # totals are a lower bound rather than implying they're exact.
    entries_missing_macros: int


class DashboardRead(BaseModel):
    day: date
    calorie_target: int | None
    calories_remaining: int | None
    totals: DayTotalsRead
    meals: dict[MealType, list[FoodEntryRead]]
    weight_on_day: WeightRead | None
    recent_weights: list[WeightRead]
