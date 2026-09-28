"""Database connection and session handling.

Rails equivalent: ActiveRecord's connection pool, which Rails sets up for you.
SQLAlchemy makes it explicit:
  - `engine`       -> the connection pool
  - `SessionLocal` -> a factory for "sessions" (a unit of work; you add/change
                      objects, then `commit()` saves them in one transaction)
  - `Base`         -> ApplicationRecord; every model inherits from it
"""

from collections.abc import Iterator

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False)

# Predictable constraint/index names, so Alembic migrations can refer to them later.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_N_label)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


def get_db() -> Iterator[Session]:
    """Open one session per request and always close it afterwards.

    `yield` hands the session to the endpoint; the code after `yield` runs
    once the request finishes. Rails does this for you behind the scenes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
