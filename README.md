# personal-nutrition
A personal nutrition application to combine WHOOP data, weight history, eating history and activity data to provide health and training insights

## Stack

- **backend/**: Python, FastAPI, SQLAlchemy, Alembic (migrations), Pydantic
- **frontend/**: Next.js, React, TypeScript
- **db**: PostgreSQL 17
- Everything runs in Docker, so you don't need Python or Node installed locally.

New to Python? See [docs/rails-to-python.md](docs/rails-to-python.md).

## Getting started

Requirements: Docker Desktop (on Windows this needs WSL 2: run `wsl --install` in an
admin terminal and restart).

```sh
cp .env.example .env        # then set a real POSTGRES_PASSWORD in .env
docker compose up --build
```

- Dashboard: http://localhost:3000
- API docs (interactive): http://localhost:8000/docs

Migrations run automatically when the backend starts.

## Everyday commands

| Task | Command | Rails equivalent |
| --- | --- | --- |
| Start everything | `docker compose up` | `bin/dev` |
| Run backend tests | `docker compose exec backend pytest` | `bin/rspec` |
| New migration from model changes | `docker compose exec backend alembic revision --autogenerate -m "add x"` | `rails g migration` |
| Apply migrations | `docker compose exec backend alembic upgrade head` | `rails db:migrate` |
| Roll back one migration | `docker compose exec backend alembic downgrade -1` | `rails db:rollback` |
| Python console | `docker compose exec backend python` | `rails console` |
| psql | `docker compose exec db psql -U nutrition nutrition` | `rails dbconsole` |
| Add a frontend package | `docker compose exec frontend npm install <pkg>` | `bundle add` |

## Layout

```text
backend/
  app/
    main.py            app setup + route mounting        (config/routes.rb)
    config.py          settings from env vars            (config/database.yml)
    database.py        engine, sessions, Base            (ApplicationRecord)
    models.py          tables: User, WeightEntry, FoodEntry   (app/models)
    schemas.py         request/response shapes           (strong params + serializers)
    deps.py            current_user, db session          (before_action)
    routers/           endpoints                         (app/controllers)
    services/          pure calculations                 (app/services)
  alembic/versions/    migrations                        (db/migrate)
  tests/               pytest tests                      (spec/)
frontend/
  app/                 pages; folders = URLs             (app/views + routes)
  components/          reusable UI pieces                (partials)
  lib/api.ts           typed API client
```

## Current scope

- Single user profile, with goal, targets and dietary notes. There's no login yet;
  the API uses the first user, and every query is scoped by `user_id` so auth can be added later.
- Weight log: one entry per day (saving again replaces it).
- Food log: entries per meal per day, with calories and optional macros.
- Dashboard: daily totals, calories remaining, meals, recent weights.

Next up (see AGENTS.md): analytics, WHOOP ingestion, TDEE estimates.
