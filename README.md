# Energy Operations Platform

## Overview

The **Energy Operations Platform** is a Python, PostgreSQL and FastAPI portfolio project for processing, validating and exposing technical energy and station data.

The project simulates a backend/data platform for technical assets such as solar parks, wind parks, battery storage systems, substations and grid connections. It is built as part of a structured transition toward backend, data and cloud-oriented software roles in industry, energy and infrastructure.

## Current Version

**Current project version:** `v0.9.0`

Current focus:

- PostgreSQL-backed FastAPI REST API
- Pydantic request and response models
- Measurement create/read/update flow
- Global and station-specific KPI endpoints
- Automated API tests with `pytest` and FastAPI `TestClient`
- Dedicated PostgreSQL test database
- Modular test structure with shared fixtures
- Documented test data strategy
- Initial Dockerfile for running the FastAPI app in a container
- `.dockerignore` for cleaner Docker build context

## Project Goal

The goal is to build a realistic backend/data project that demonstrates:

- relational data modeling with PostgreSQL,
- API development with FastAPI,
- request and response validation with Pydantic,
- database-backed REST endpoints,
- automated API testing,
- deterministic test data handling,
- KPI and analytics logic for technical measurement data,
- gradual preparation for Docker, Docker Compose, cloud deployment and portfolio presentation.

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
├── .env.example           # example environment configuration
├── Dockerfile             # initial FastAPI container build definition
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
| `docs/deployment_notes.md` | Docker status, build/run commands and deployment-related notes |
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
| Containerization | Dockerfile, Docker image, Docker container, port mapping |
| Development workflow | Git, GitHub, branches, commits, version tags, GitHub pre-releases |
| Future scope | Docker Compose, Azure fundamentals, security basics, deployment readiness |

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
DB_NAME=energy_operations
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

Automated tests use a dedicated test database:

```text
energy_operations_test
```

The test database is configured in `tests/conftest.py` before the FastAPI app is imported.

## How to Run Locally

### Install dependencies

```bash
py -m pip install -r requirements.txt
```

### Run the FastAPI backend

```bash
py run_api.py
```

Then open:

```text
http://127.0.0.1:8000/docs
```

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

Combined marker examples:

```bash
py -m pytest -v -m "post and validation"
py -m pytest -v -m "kpi and not validation"
```

Detailed testing notes are documented in [`docs/test_strategy.md`](docs/test_strategy.md).

## Docker Status

Docker support started in `v0.9.0`.

The current Docker setup can build and run the FastAPI application container:

```bash
docker build -t energy-operations-api:v0.9.0 .
docker run --name energy-api-test -p 8000:8000 energy-operations-api:v0.9.0
```

Then open:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
```

At this stage, PostgreSQL is not yet containerized. Database-backed endpoints may require additional environment configuration when the API runs inside Docker. Docker Compose for API + PostgreSQL is planned as the next deployment-related step.

Detailed Docker notes are documented in [`docs/deployment_notes.md`](docs/deployment_notes.md).

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
| `sql/seed_data.sql` | Development seed data |
| `sql/test_seed_data.sql` | Deterministic test seed data |
| `sql/example_queries.sql` | SQL learning and exploration queries |

## Version History

Current version highlights:

| Version | Status | Main result |
|---|---|---|
| `v0.9.0` | current | Added initial Dockerfile and Docker build/run workflow for the FastAPI app |
| `v0.8` | released | Testing, robustness and API consistency pre-release |
| `v0.8.6` | completed | Centralized API not-found handling |
| `v0.8.5` | completed | Documented and refined test data strategy |
| `v0.8.4` | completed | Split API tests into focused modules |
| `v0.8.3` | completed | Added pytest markers for API test groups |

Full version details are documented in [`docs/version_history.md`](docs/version_history.md).

## Roadmap

Next project steps:

1. Extend Docker support with Docker Compose for FastAPI + PostgreSQL.
2. Clarify environment handling for local Docker runs and future Compose setup.
3. Add setup documentation and an architecture diagram for portfolio readiness.
4. Add security basics such as API key concepts and secret handling.
5. Prepare a portfolio MVP release suitable for applications and interviews.

## Portfolio Positioning

This project is not a generic tutorial app. It is designed to connect engineering domain knowledge with backend, database, API, testing and later cloud skills.

The project demonstrates a practical learning path from local data processing to a structured backend system with database integration, API contracts, automated tests, analytics-oriented endpoints and first deployment-readiness steps.
