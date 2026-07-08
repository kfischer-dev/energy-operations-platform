# Version History

This document tracks the main learning and implementation milestones of the Energy Operations Platform.

The project uses small, explainable versions so the GitHub history remains easy to follow.

## Current Version

| Version | Status | Summary |
|---|---|---|
| `v0.8.6` | current | Centralized API not-found handling with small helper functions |

## Version Timeline

| Version | Status | Main result | Learning value |
|---|---|---|---|
| `v0.1` | completed | Python dictionaries with station data, first statistics and classification logic | Python syntax, functions, data structures |
| `v0.2` | completed | File handling, TXT/CSV workflows and basic error handling | File processing, robustness, data flow |
| `v0.3` | completed | `Station` class and CSV-to-object workflow | OOP, encapsulation, module boundaries |
| `v0.3.2` | completed | Logging, README and first GitHub-ready structure | Traceability and project documentation |
| `v0.4` | completed | PostgreSQL schema, seed data, SQL queries, Python DB access and project reorganization | Relational data modeling and DB integration |
| `v0.4.1` | completed | DB result mapping from tuples into dictionaries | API/JSON preparation |
| `v0.5` | completed | First FastAPI app with general, station and measurement read endpoints | Backend, HTTP, JSON and OpenAPI basics |
| `v0.5.1` | completed | Swagger/OpenAPI metadata, tags and parameter descriptions | API documentation and endpoint clarity |
| `v0.5.2` | completed | Pydantic response models | Typed API contracts |
| `v0.5.3` | completed | First pytest/TestClient API tests | Automated API testing |
| `v0.6.0` | completed | `POST /measurements` with `INSERT ... RETURNING` | Write API and database insert flow |
| `v0.6.1` | completed | Input validation for measurement creation | Pydantic `Field`, `Literal` and 422 behavior |
| `v0.6.2` | completed | `GET /measurements/{measurement_id}` and create-then-read flow | Detail resources and readback tests |
| `v0.6.3` | completed | `PATCH /measurements/{measurement_id}` for `quality_status` | Update flow and data-quality handling |
| `v0.7.0` | completed | `GET /kpis/measurements` | Global analytics, SQL aggregation, valid-only KPI filtering |
| `v0.7.1` | completed | `GET /stations/{station_id}/kpis` | Station-specific analytics and empty-KPI behavior |
| `v0.8.0` | completed | Dedicated isolated test database setup | Safer automated tests and environment separation |
| `v0.8.1` | completed | Deterministic KPI assertions | Stable exact-value KPI tests |
| `v0.8.2` | completed | Improved POST/PATCH test structure | Clear create/read/update test flows |
| `v0.8.3` | completed | pytest markers for API test groups | Targeted test execution by category |
| `v0.8.4` | completed | Split API tests into focused modules | Better test organization and maintainability |
| `v0.8.5` | completed | Documented test data strategy and reorganized documentation | Clear separation between user docs and developer docs |
| `v0.8.6` | current | Centralized API not-found handling with `get_station_or_404()` and `get_measurement_or_404()` | Reduced duplicated 404 logic and improved API robustness |

## v0.8.x Focus

The `v0.8.x` series focuses on robustness rather than new business features.

Key improvements:

- isolated test database,
- deterministic test seed data,
- exact KPI assertions,
- improved POST/PATCH flow tests,
- pytest markers,
- modular test files,
- shared test fixtures,
- documented test data strategy,
- clearer documentation structure,
- centralized station and measurement not-found handling.

## Current Documentation Split Introduced in v0.8.5

| Document | Role |
|---|---|
| `README.md` | concise project overview and portfolio entry point |
| `docs/api_reference.md` | endpoint behavior and API contracts |
| `docs/database_notes.md` | database schema, SQL files and database layer notes |
| `docs/test_strategy.md` | test database, fixtures, markers and test data rules |
| `docs/version_history.md` | project versions and learning milestones |

## Next Planned Work

Recommended next versions:

| Version | Planned focus |
|---|---|
| `v0.8.7` | route/module organization decision, possibly router preparation |
| `v0.9.0` | Docker / Docker Compose preparation |
| `v1.0` | portfolio MVP with API, DB, tests, Docker, documentation and architecture overview |
