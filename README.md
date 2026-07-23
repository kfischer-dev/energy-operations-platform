# Energy Operations Platform

## Overview

The **Energy Operations Platform** is a backend and data portfolio project for modeling, validating, analyzing and exposing operational energy data.

It combines PostgreSQL, FastAPI, Pydantic, pytest and Docker Compose with a growing energy-domain model. The current backend supports regional assets, reusable technical classifications, interval power and energy measurements, storage specifications and valid-only KPI calculations.

## Current Version

**`v0.10.0 – Energy Domain Foundation`**

Main additions:

- regions and stable region codes,
- reusable asset types and capability flags,
- producer, consumer, storage and grid roles,
- enriched asset master data,
- power, energy and interval-based measurements,
- one-to-one storage specifications,
- compact list responses and detailed resource responses,
- migrated POST, PATCH, KPI and automated test flows.

## Project Goal

The project demonstrates practical backend and data engineering with visible energy-domain value:

- relational PostgreSQL modeling,
- typed REST APIs with FastAPI and Pydantic,
- database-backed read and write operations,
- deterministic API and KPI testing,
- reproducible local startup with Docker Compose,
- later simulation, weather influence, energy balance and recommendations.

## Architecture

```text
Client / Swagger UI
        |
        v
FastAPI + Pydantic
        |
        v
Python database access layer
        |
        v
PostgreSQL
  ├── regions
  ├── asset_types
  ├── assets
  ├── measurements
  └── storage_specs
```

## Current API

### General

- `GET /`
- `GET /health`

### Assets

- `GET /assets`
- `GET /assets?asset_type=...`
- `GET /assets/{asset_id}`

### Measurements

- `GET /measurements`
- `GET /measurements?limit=...`
- `GET /assets/{asset_id}/measurements`
- `GET /measurements/{measurement_id}`
- `POST /measurements`
- `PATCH /measurements/{measurement_id}`

List endpoints use compact summary contracts. Detail, POST and PATCH endpoints return complete resource contracts.

### KPIs

- `GET /kpis/measurements`
- `GET /assets/{asset_id}/kpis`

KPIs include valid measurement count, average/minimum/maximum active power, total interval energy and the latest valid timestamp.

## Technology Stack

| Area | Technologies |
|---|---|
| Backend | Python 3.14, FastAPI, Pydantic, OpenAPI |
| Database | PostgreSQL 18, psycopg 3 |
| Testing | pytest, FastAPI TestClient, dedicated test database |
| Deployment | Docker, Docker Compose, health checks, volumes |
| Workflow | Git, GitHub, feature branches and semantic version tags |

## Quick Start

Create `.env` from `.env.example`, then start the full local stack:

```bash
docker compose up --build
```

Open:

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/health
```

Run without Docker:

```bash
py -m pip install -r requirements.txt
py run_api.py
```

Run the automated test suite:

```bash
py -m pip install -r requirements-dev.txt
py -m pytest -v
```

Recreate the Docker development database after schema changes:

```bash
docker compose down -v
docker compose up --build
```

> This deletes the persistent development database volume.

## Database Model

| Table | Purpose |
|---|---|
| `regions` | Schematic model regions such as `DE-NORTH` |
| `asset_types` | Reusable roles and technical capability flags |
| `assets` | Producer, consumer, storage and grid master data |
| `measurements` | Interval active power and energy time series |
| `storage_specs` | Static battery-storage specifications |

Development seeds represent four German model regions. Deterministic test seeds provide known valid, invalid, estimated and empty-data scenarios.

## Testing

The current suite contains **40 automated tests** across:

- general endpoints,
- asset summary/detail behavior,
- measurement reads, POST and PATCH,
- validation and not-found behavior,
- exact global and asset-specific KPIs,
- exclusion of invalid and estimated measurements.

## Documentation

| Document | Purpose |
|---|---|
| [`docs/api_reference.md`](docs/api_reference.md) | Endpoint and API contracts |
| [`docs/data_dictionary.md`](docs/data_dictionary.md) | Domain and field definitions |
| [`docs/database_notes.md`](docs/database_notes.md) | Schema and database layer |
| [`docs/test_strategy.md`](docs/test_strategy.md) | Fixtures, seeds and test rules |
| [`docs/deployment_notes.md`](docs/deployment_notes.md) | Docker and local environment |
| [`docs/version_history.md`](docs/version_history.md) | Project milestones |

## Repository Structure

```text
energy-operations-platform/
├── docs/
├── sql/
├── src/
├── tests/
├── compose.yaml
├── Dockerfile
├── pytest.ini
├── requirements.txt
├── run_api.py
└── README.md
```

Private notes, logs, environments, `.env` files and archives are excluded from Git and the Docker build context.

## Roadmap

1. Simulation foundation with configurable periods and intervals.
2. Producer, consumer, storage and grid profiles.
3. Regional weather simulation and weather-driven generation.
4. Global and regional energy balance.
5. Rule-based operational recommendations.
6. React dashboard with map, charts and live/history views.
7. Azure deployment after the backend MVP is stable.

## Portfolio Positioning

The project is designed as more than a generic CRUD API. It combines backend engineering, relational modeling, automated quality controls, reproducible infrastructure and a domain model that can support realistic energy simulation and operational analytics.
