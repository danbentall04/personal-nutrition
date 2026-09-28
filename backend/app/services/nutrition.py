"""Nutrition calculations.

These are pure functions: no database or HTTP, just data in and results out.
That keeps them easy to test and makes them the place for the deterministic
maths (see AGENTS.md). Rails equivalent: a plain Ruby object in app/services/.

Totals are derived data: they're calculated from the raw food entries on
request and never stored, so they can't get out of sync.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from app.models import FoodEntry


# A dataclass is a lightweight value object, like a Ruby Struct.
@dataclass(frozen=True)
class DayTotals:
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    entries_missing_macros: int


def summarise_day(entries: Sequence[FoodEntry]) -> DayTotals:
    # `sum(x for x in ...)` is Ruby's `entries.sum { |e| ... }`.
    # `e.protein_g or 0` treats an unknown value (None) as 0 for the total.
    return DayTotals(
        calories=sum(e.calories for e in entries),
        protein_g=round(sum(e.protein_g or 0 for e in entries), 1),
        carbs_g=round(sum(e.carbs_g or 0 for e in entries), 1),
        fat_g=round(sum(e.fat_g or 0 for e in entries), 1),
        entries_missing_macros=sum(
            1 for e in entries if e.protein_g is None or e.carbs_g is None or e.fat_g is None
        ),
    )
