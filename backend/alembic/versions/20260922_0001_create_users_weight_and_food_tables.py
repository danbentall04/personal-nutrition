"""create users, weight_entries and food_entries

Revision ID: 0001
Revises:
Create Date: 2026-09-22

Rails equivalent: db/migrate/20260922000001_create_initial_tables.rb.
Future migrations can be generated from model changes with:
    docker compose exec backend alembic revision --autogenerate -m "describe change"
Always read a generated migration before running it.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def timestamps() -> list[sa.Column]:
    """Rails: `t.timestamps`"""
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("sex", sa.String(20), nullable=True),
        sa.Column("height_cm", sa.Numeric(4, 1), nullable=True),
        sa.Column("goal", sa.String(20), server_default="maintain", nullable=False),
        sa.Column("target_weight_kg", sa.Numeric(5, 2), nullable=True),
        sa.Column("daily_calorie_target", sa.Integer(), nullable=True),
        sa.Column("dietary_notes", sa.Text(), nullable=True),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.CheckConstraint("sex IN ('female', 'male')", name="ck_users_sex"),
        sa.CheckConstraint("goal IN ('lose', 'maintain', 'gain')", name="ck_users_goal"),
    )

    op.create_table(
        "weight_entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("measured_on", sa.Date(), nullable=False),
        sa.Column("weight_kg", sa.Numeric(5, 2), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_weight_entries"),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_weight_entries_user_id_users", ondelete="CASCADE"
        ),
        sa.UniqueConstraint("user_id", "measured_on", name="uq_weight_entries_user_id_measured_on"),
        sa.CheckConstraint("weight_kg > 0", name="ck_weight_entries_weight_positive"),
    )

    op.create_table(
        "food_entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("eaten_on", sa.Date(), nullable=False),
        sa.Column("meal", sa.String(20), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("quantity", sa.String(100), nullable=True),
        sa.Column("calories", sa.Integer(), nullable=False),
        sa.Column("protein_g", sa.Numeric(6, 1), nullable=True),
        sa.Column("carbs_g", sa.Numeric(6, 1), nullable=True),
        sa.Column("fat_g", sa.Numeric(6, 1), nullable=True),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_food_entries"),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_food_entries_user_id_users", ondelete="CASCADE"
        ),
        sa.CheckConstraint(
            "meal IN ('breakfast', 'lunch', 'dinner', 'snack')", name="ck_food_entries_meal_type"
        ),
        sa.CheckConstraint("calories >= 0", name="ck_food_entries_calories_non_negative"),
    )
    op.create_index("ix_food_entries_user_id_eaten_on", "food_entries", ["user_id", "eaten_on"])


def downgrade() -> None:
    op.drop_index("ix_food_entries_user_id_eaten_on", table_name="food_entries")
    op.drop_table("food_entries")
    op.drop_table("weight_entries")
    op.drop_table("users")
