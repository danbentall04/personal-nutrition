# Personal Nutrition & Physiology App

## Purpose

Build a personal nutrition and physiology optimisation app. This is **not a WHOOP clone**. WHOOP is a data source used alongside food, weight and goal data to provide personalised analysis and recommendations.

The core loop is:

**Eat → measure → learn → adjust**

The long-term goal is to answer questions such as:

> Given my current weight trend, goals, activity and physiological state, what should I eat today?

## Core Data

The app will combine:

* WHOOP: sleep, recovery, HRV, RHR, workouts, strain and energy expenditure
* Food/calorie/macro logs
* Weight history
* User goals (lose, maintain or gain)
* Dietary preferences and constraints

Treat wearable calorie expenditure as an **estimate**, not ground truth.

## Architecture Principles

* Use deterministic/statistical code for calculations.
* Use the LLM for natural-language interaction, explanations and meal suggestions.
* Do **not** ask the LLM to calculate critical nutritional metrics.
* Store raw external data separately from derived analytics.
* Make external data ingestion idempotent.
* Represent uncertainty rather than false precision.
* Start as a modular monolith; do not introduce microservices unnecessarily.

Target flow:

```text
WHOOP + Food + Weight
        ↓
     PostgreSQL
        ↓
 Analytics / Energy Model
        ↓
 Structured Insights
        ↓
       LLM
        ↓
Recommendations / UI
```

## Technology Goals

This project is partly a learning project.

Preferred stack:

* Python
* FastAPI
* Pydantic
* PostgreSQL
* SQLAlchemy or SQLModel
* Pandas for analysis
* TimescaleDB if useful for time-series data
* Next.js + React + TypeScript
* Docker
* GitHub Actions

Use this project to improve Python, data analysis, PostgreSQL and TypeScript skills.

## Development Priorities

Build incrementally:

1. Weight, food and goal tracking
2. Basic calorie/macro analytics
3. WHOOP OAuth and data ingestion
4. Weight trends and estimated energy balance/TDEE
5. Personalised calorie targets
6. Meal recommendations
7. LLM-powered conversational features

Avoid over-engineering early.

## Security

This app contains sensitive personal health data.

* Never commit `.env` files, OAuth tokens, API keys or real user data.
* Keep the database private.
* Use environment variables/secrets.
* Validate external API input.
* Maintain backups.

## Coding Guidance

Prefer simple, explicit and maintainable code over unnecessary abstractions.

When implementing features, consider:

* What raw data is the source of truth?
* What derived data can be recalculated?
* What calculations should be deterministic?
* Where does uncertainty exist?

The app should become a personalised model of the user's nutrition and physiology over time.
