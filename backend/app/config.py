"""App settings, read from environment variables.

Rails equivalent: config/database.yml + ENV["..."] lookups. Pydantic reads the
env var DATABASE_URL into `settings.database_url` and fails at startup if it's
missing, instead of failing later on the first query.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str


settings = Settings()
