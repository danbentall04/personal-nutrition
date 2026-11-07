"""Rails equivalent: a model/service spec. Run with `pytest` (like `rspec`)."""

from app.models import FoodEntry, MealType
from app.services.nutrition import summarise_day


def make_entry(calories: int, protein=None, carbs=None, fat=None) -> FoodEntry:
    return FoodEntry(
        meal=MealType.LUNCH,
        name="Test food",
        calories=calories,
        protein_g=protein,
        carbs_g=carbs,
        fat_g=fat,
    )


def test_empty_day_is_all_zeros():
    totals = summarise_day([])
    assert totals.calories == 0
    assert totals.protein_g == 0
    assert totals.entries_missing_macros == 0


def test_sums_calories_and_macros():
    totals = summarise_day(
        [make_entry(500, protein=30, carbs=50, fat=20), make_entry(250, protein=10.5, carbs=20, fat=5)]
    )
    assert totals.calories == 750
    assert totals.protein_g == 40.5
    assert totals.carbs_g == 70
    assert totals.fat_g == 25


def test_missing_macros_are_counted_not_hidden():
    totals = summarise_day([make_entry(500, protein=30, carbs=50, fat=20), make_entry(300)])
    assert totals.calories == 800
    assert totals.protein_g == 30
    assert totals.entries_missing_macros == 1
