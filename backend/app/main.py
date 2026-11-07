"""App entry point. Rails equivalent: config/application.rb + config/routes.rb.

Run by uvicorn (our Puma): `uvicorn app.main:app` means "in the module
app/main.py, serve the object called `app`".
"""

from fastapi import FastAPI

from app.routers import dashboard, food, profile, weights

app = FastAPI(title="Personal Nutrition API")

# Each router is like a controller plus its routes; all mounted under /api.
app.include_router(profile.router, prefix="/api")
app.include_router(weights.router, prefix="/api")
app.include_router(food.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")


@app.get("/api/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
