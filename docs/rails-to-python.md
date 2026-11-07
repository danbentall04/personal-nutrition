# Rails → Python/FastAPI cheat sheet

A quick map from Rails concepts to their equivalents in this codebase.

## The big picture

| Rails | Here | Notes |
| --- | --- | --- |
| Rails (the framework) | FastAPI | FastAPI only does the HTTP/API layer. The other pieces are separate libraries. |
| ActiveRecord | SQLAlchemy | The ORM. |
| `db/migrate`, `rails db:migrate` | Alembic | Can *autogenerate* migrations by comparing models to the DB. |
| Strong params + serializers | Pydantic (`schemas.py`) | One class validates input *and* shapes output. |
| ERB views | Next.js/React (`frontend/`) | Separate app that calls the API with JSON. |
| Puma | uvicorn | The web server. |
| Gemfile / `bundle install` | `requirements.txt` / `pip install -r` | |
| RSpec | pytest | Tests are plain functions named `test_*` using `assert`. |
| `rails console` | `python` (in the backend container) | |

## Models

```ruby
# Rails
class FoodEntry < ApplicationRecord
  belongs_to :user
  enum :meal, { breakfast: "breakfast", lunch: "lunch", ... }
end
```

```python
# SQLAlchemy (app/models.py)
class FoodEntry(TimestampMixin, Base):
    __tablename__ = "food_entries"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    meal: Mapped[MealType] = mapped_column(enum_column(MealType, "meal_type"))
    user: Mapped[User] = relationship(back_populates="food_entries")
```

- Columns are declared on the class. There's no separate schema.rb.
- `Mapped[str | None]` means nullable; `Mapped[str]` means NOT NULL.
- `(TimestampMixin, Base)` is multiple inheritance, similar to including a module.

## Queries

| ActiveRecord | SQLAlchemy 2.0 |
| --- | --- |
| `FoodEntry.find_by(id: 5)` | `db.get(FoodEntry, 5)` |
| `user.food_entries.where(eaten_on: day)` | `db.scalars(select(FoodEntry).where(FoodEntry.user_id == user.id, FoodEntry.eaten_on == day)).all()` |
| `.order(measured_on: :desc).limit(14)` | `.order_by(WeightEntry.measured_on.desc()).limit(14)` |
| `.first` | `.first()` |
| `record.save!` | `db.add(record); db.commit()` |
| `record.update!(attrs)` | set attributes, then `db.commit()` |
| `record.destroy!` | `db.delete(record); db.commit()` |
| `record.reload` | `db.refresh(record)` |

The `db` object is a **Session**. You change objects, and `commit()` saves them all in one
transaction. Rails saves each record on its own when you call `save`.

## Controllers and routes

```ruby
# Rails
resources :food_entries, only: [:create]

def create
  entry = current_user.food_entries.create!(food_entry_params)
  render json: entry, status: :created
end
```

```python
# FastAPI (app/routers/food.py)
@router.post("", response_model=FoodEntryRead, status_code=201)
def create_food_entry(payload: FoodEntryCreate, user: CurrentUser, db: DbSession):
    entry = FoodEntry(user_id=user.id, **payload.model_dump())
    db.add(entry)
    db.commit()
    return entry
```

- `@router.post(...)` is a **decorator**. It registers the function as the handler for that
  route, so the route and the action sit together instead of in routes.rb.
- Parameters are filled in automatically based on their type:
  - path segments (`/{entry_id}`) → path params
  - simple types not in the path (`day: date`) → query string (`?day=...`)
  - Pydantic models (`payload: FoodEntryCreate`) → JSON body, validated
  - `Depends(...)` types (`user: CurrentUser`) → computed first, like `before_action`
- Invalid input returns a 422 with details before your code runs.

## Python syntax that differs from Ruby

| Ruby | Python |
| --- | --- |
| `nil` | `None` |
| `arr.map { \|x\| x * 2 }` | `[x * 2 for x in arr]` (list comprehension) |
| `arr.select { \|x\| x > 1 }` | `[x for x in arr if x > 1]` |
| `arr.sum { \|e\| e.calories }` | `sum(e.calories for e in arr)` |
| `arr.find { \|x\| ... }` | `next((x for x in arr if ...), None)` |
| `hash.to_h { \|k\| [k, v] }` | `{k: v for k in keys}` (dict comprehension) |
| `a \|\| b` | `a or b` |
| `x ? a : b` | `a if x else b` |
| `def method(a, b: 1)` | `def method(a, b=1):` |
| `**opts` (keyword splat) | `**kwargs` / `Model(**some_dict)` |
| `Struct.new(:a, :b)` | `@dataclass class Thing: a: int; b: int` |
| `attr.send(:"#{k}=", v)` | `setattr(obj, k, v)` |
| `require "x"` | `from x import y` |
| blocks with `ensure` | `try: ... finally: ...` |
| `yield` to a block | `yield` in a generator (e.g. `get_db`) |

Type hints (`def f(day: date) -> str:`) are optional in plain Python, but FastAPI and
SQLAlchemy read them to decide behaviour, so this codebase always uses them.
