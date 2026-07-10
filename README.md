# Energy Operations Platform

## Overview

The **Energy Operations Platform** is a Python, PostgreSQL and FastAPI portfolio project for processing, validating and exposing technical energy and station data.

The project is evolving into a small backend platform for the energy sector. In addition to the existing API, database, tests and KPI functions, the next development phases will focus on realistic energy-domain data, simulation, production and consumption profiles, energy balances and actionable recommendations.

## Current Version

**Current project version:** `v0.9.2`

Current focus:

- PostgreSQL-backed FastAPI REST API
- Pydantic request and response models
- Measurement create/read/update flow
- Global and station-specific KPI endpoints
- Automated API tests with `pytest` and FastAPI `TestClient`
- Dedicated PostgreSQL test database
- Modular test structure with shared fixtures
- Docker image for the FastAPI application
- Docker Compose setup for FastAPI and PostgreSQL
- Automatic schema and development seed initialization for a new database volume
- Persistent PostgreSQL data through a named Docker volume

## Project Goal

The goal is to build a realistic backend/data project that demonstrates:

- relational data modeling with PostgreSQL,
- API development with FastAPI,
- request and response validation with Pydantic,
- database-backed REST endpoints,
- automated API testing,
- deterministic test data handling,
- KPI and analytics logic for technical measurement data,
- reproducible local startup with Docker and Docker Compose,
- later energy-domain simulation, balances and recommendations.

The project should not add technologies only for demonstration purposes. New features should provide visible domain value and support the later dashboard.

## Repository Structure

```text
energy-operations-platform/
├── data/                  # legacy CSV input data
├── demos/                 # legacy demo workflows
├── docs/                  # developer documentation
├── sql/                   # schema, seed data and example queries
├── src/                   # application source code
├── tests/                 # automated API tests
├── .dockerignore          # excludes local/private files from Docker build context
├── .env.example           # local and Compose environment example
├── compose.yaml           # FastAPI + PostgreSQL development environment
├── Dockerfile             # FastAPI container image definition
├── pytest.ini             # pytest marker configuration
├── README.md              # project overview and quick start
├── requirements.txt       # Python dependencies
└── run_api.py             # local API startup helper
```

## Documentation Map

The documentation is intentionally split to avoid an overloaded README.

| Document | Purpose |
|---|---|
| `README.md` | Portfolio-oriented project overview, quick start, feature summary and links |
| `docs/api_reference.md` | API endpoint overview, request/response models and error behavior |
| `docs/database_notes.md` | Database schema, SQL files, database access layer and data-quality rules |
| `docs/test_strategy.md` | Test database, fixtures, markers, reset rules and test data strategy |
| `docs/deployment_notes.md` | Dockerfile, Docker Compose, environment handling and startup notes |
| `docs/version_history.md` | Version-by-version project history and learning milestones |

## Technologies Used

| Area | Tools / Concepts |
|---|---|
| Language | Python |
| Backend | FastAPI, REST, JSON, OpenAPI/Swagger |
| Database | PostgreSQL, SQL, primary keys, foreign keys, joins, aggregations |
| Validation | Pydantic, request models, response models, field constraints, literal values |
| Testing | pytest, FastAPI TestClient, fixtures, test markers, dedicated test database |
| Configuration | `.env`, environment variables, `.env.example` |
| Containerization | Dockerfile, Docker Compose, images, containers, service networking, volumes |
| Development workflow | Git, GitHub, branches, commits, version tags, GitHub pre-releases |
| Planned domain scope | Regions, producers, consumers, simulation, weather, energy balance, recommendations |

## Current Features

### General API

- `GET /`
- `GET /health`

### Station API

- `GET /stations`
- `GET /stations?station_type=...`
- `GET /stations/{station_id}`

### Measurement API

- `GET /measurements`
- `GET /measurements?limit=...`
- `GET /measurements/{measurement_id}`
- `GET /stations/{station_id}/measurements`
- `GET /stations/{station_id}/measurements?limit=...`
- `POST /measurements`
- `PATCH /measurements/{measurement_id}`

### KPI / Analytics API

- `GET /kpis/measurements`
- `GET /stations/{station_id}/kpis`

Detailed endpoint behavior is documented in [`docs/api_reference.md`](docs/api_reference.md).

## Database Model

The current database model contains two main tables:

- `stations` for energy asset master data
- `measurements` for technical measurement values linked to stations

The measurement table includes `quality_status`, which is used by KPI endpoints to exclude invalid values from analytics calculations.

Detailed database notes are documented in [`docs/database_notes.md`](docs/database_notes.md).

## Environment Configuration

Create a local `.env` file based on `.env.example`.

```env
# FastAPI database connection
DB_NAME=energy_operations
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=5432

# PostgreSQL container initialization
POSTGRES_DB=energy_operations
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here
```

For Docker Compose, the API service overrides `DB_HOST` with the PostgreSQL service name `db`. The API and database communicate over the internal Compose network on PostgreSQL port `5432`.

The database is exposed on host port `5433` to avoid a conflict with an existing local PostgreSQL installation on `5432`.

Automated tests continue to use the dedicated test database:

```text
energy_operations_test
```

## How to Run Locally

### Install dependencies

```bash
py -m pip install -r requirements.txt
```

### Run the FastAPI backend without Docker

```bash
py run_api.py
```

Then open:

```text
http://127.0.0.1:8000/docs
```

### Run the full system with Docker Compose

```bash
docker compose up --build
```

Then open:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/stations
```

Run in the background:

```bash
docker compose up --build -d
```

Stop the services:

```bash
docker compose down
```

Remove the PostgreSQL volume and recreate the database from schema and seed files:

```bash
docker compose down -v
docker compose up --build
```

> `docker compose down -v` deletes the persistent database volume. Use it deliberately.

### Run automated tests

Run the full test suite:

```bash
py -m pytest -v
```

Run selected marker groups:

```bash
py -m pytest -v -m post
py -m pytest -v -m patch
py -m pytest -v -m kpi
py -m pytest -v -m validation
```

Detailed testing notes are documented in [`docs/test_strategy.md`](docs/test_strategy.md).

## Docker Status

Docker support is operational for the local development environment as of `v0.9.2`.

The Compose setup provides:

- an `api` service built from the project `Dockerfile`,
- a `db` service based on PostgreSQL 18,
- internal service-to-service networking through `DB_HOST=db`,
- host access to the database through port `5433`,
- automatic schema and seed loading for a newly created database volume,
- persistent PostgreSQL storage through the `db_data` volume,
- PostgreSQL readiness checking with delayed API startup until the database is healthy.

Detailed setup and troubleshooting notes are documented in [`docs/deployment_notes.md`](docs/deployment_notes.md).

## Testing Summary

The current test setup uses:

- a dedicated PostgreSQL test database,
- deterministic seed data from `sql/test_seed_data.sql`,
- session-level database reset before test execution,
- explicit `reset_db` fixture for exact KPI tests,
- test-created data for POST and PATCH flows,
- pytest markers for targeted execution,
- modular test files for general, station, measurement and KPI endpoints.

## SQL Files

| File | Purpose |
|---|---|
| `sql/schema.sql` | Creates the core database schema |
| `sql/seed_data.sql` | Development seed data and initial Compose data |
| `sql/test_seed_data.sql` | Deterministic test seed data |
| `sql/example_queries.sql` | SQL learning and exploration queries |

## Version History

Current version highlights:

| Version | Status | Main result |
|---|---|---|
| `v0.9.2` | current | Added PostgreSQL health checking and delayed API startup until the database is ready |
| `v0.9.1` | completed | Added Docker Compose for FastAPI + PostgreSQL with initialization and persistent data |
| `v0.9.0` | completed | Added initial Dockerfile and standalone API container workflow |
| `v0.8` | released | Testing, robustness and API consistency pre-release |
| `v0.8.6` | completed | Centralized API not-found handling |
| `v0.8.5` | completed | Documented and refined test data strategy |

Full version details are documented in [`docs/version_history.md`](docs/version_history.md).

## Roadmap

Next project steps:

1. Extend the energy domain with regions, producers, consumers and capacity data.
2. Build backfill and accelerated live-simulation modes.
3. Add simplified weather-driven production and realistic consumption profiles.
4. Calculate global and regional energy balances and rule-based recommendations.
5. Add a React dashboard after the backend MVP is stable.
6. Add Azure deployment later, after the domain-oriented backend provides enough value.

## Portfolio Positioning

This project is not intended to remain a generic CRUD or tutorial API. It connects engineering domain knowledge with backend, database, API, testing and deployment skills.

The current platform already demonstrates a structured backend foundation. The next phases will turn it into a small, explainable energy operations system with simulated operating data, production and consumption behavior, balances and recommendations that can later be visualized in a dashboard.
