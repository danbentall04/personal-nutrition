"""Database tables: the raw data that everything else is calculated from.

Rails equivalent: app/models/*.rb and db/schema.rb in one place. In Rails the
columns live in schema.rb and the model class only holds behaviour. Here the
class declares the columns too, and Alembic (our `rails db:migrate`) compares
these classes with the database to generate migrations.

`Mapped[str | None]` means the column is nullable; `Mapped[str]` means NOT NULL.
"""

import enum
from datetime import date, datetime

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# Rails: `enum :goal, { lose: "lose", maintain: "maintain", gain: "gain" }`
class Goal(enum.StrEnum):
    LOSE = "lose"
    MAINTAIN = "maintain"
    GAIN = "gain"


class Sex(enum.StrEnum):
    """Biological sex, used later by BMR equations (e.g. Mifflin-St Jeor)."""

    FEMALE = "female"
    MALE = "male"


class MealType(enum.StrEnum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


def enum_column(enum_cls: type[enum.StrEnum], name: str) -> Enum:
    # Stored as VARCHAR + CHECK constraint instead of a native Postgres ENUM,
    # because native ENUMs are awkward to change in later migrations.
    return Enum(
        enum_cls,
        name=name,
        length=20,
        native_enum=False,
        create_constraint=True,
        values_callable=lambda members: [m.value for m in members],
    )


class TimestampMixin:
    """Rails: `t.timestamps` in a migration."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str | None] = mapped_column(String(255), unique=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date)
    sex: Mapped[Sex | None] = mapped_column(enum_column(Sex, "sex"))
    # NUMERIC stores exact decimals in Postgres; asdecimal=False gives us a
    # plain Python float back, which is easier to work with and to send as JSON.
    height_cm: Mapped[float | None] = mapped_column(Numeric(4, 1, asdecimal=False))
    goal: Mapped[Goal] = mapped_column(
        enum_column(Goal, "goal"), default=Goal.MAINTAIN, server_default=Goal.MAINTAIN.value
    )
    target_weight_kg: Mapped[float | None] = mapped_column(Numeric(5, 2, asdecimal=False))
    daily_calorie_target: Mapped[int | None]
    dietary_notes: Mapped[str | None] = mapped_column(Text)

    # Rails: `has_many :weight_entries, dependent: :destroy`
    weight_entries: Mapped[list["WeightEntry"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    food_entries: Mapped[list["FoodEntry"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class WeightEntry(TimestampMixin, Base):
    __tablename__ = "weight_entries"
    __table_args__ = (
        # One weigh-in per user per day. Saving twice for a day updates it.
        # Rails: `validates :measured_on, uniqueness: { scope: :user_id }` + a unique index.
        UniqueConstraint("user_id", "measured_on"),
        CheckConstraint("weight_kg > 0", name="weight_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    # Rails: `belongs_to :user` / `t.references :user, foreign_key: true`
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    measured_on: Mapped[date] = mapped_column(Date)
    weight_kg: Mapped[float] = mapped_column(Numeric(5, 2, asdecimal=False))
    note: Mapped[str | None] = mapped_column(Text)

    user: Mapped[User] = relationship(back_populates="weight_entries")


class FoodEntry(TimestampMixin, Base):
    __tablename__ = "food_entries"
    __table_args__ = (
        # The dashboard always asks for "this user's entries on this day".
        Index("ix_food_entries_user_id_eaten_on", "user_id", "eaten_on"),
        CheckConstraint("calories >= 0", name="calories_non_negative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    eaten_on: Mapped[date] = mapped_column(Date)
    meal: Mapped[MealType] = mapped_column(enum_column(MealType, "meal_type"))
    name: Mapped[str] = mapped_column(String(200))
    quantity: Mapped[str | None] = mapped_column(String(100))  # free text, e.g. "150 g"
    calories: Mapped[int]
    # Macros are optional: often you only know the calories. Null means "unknown",
    # which is different from 0.
    protein_g: Mapped[float | None] = mapped_column(Numeric(6, 1, asdecimal=False))
    carbs_g: Mapped[float | None] = mapped_column(Numeric(6, 1, asdecimal=False))
    fat_g: Mapped[float | None] = mapped_column(Numeric(6, 1, asdecimal=False))

    user: Mapped[User] = relationship(back_populates="food_entries")
