# Energy Operations Platform

## Overview

The **Energy Operations Platform** is a backend and data portfolio project for modeling, validating, simulating, analyzing and exposing operational energy data.

It combines PostgreSQL, FastAPI, Pydantic, pytest and Docker Compose with a domain model for technical energy assets. The current backend supports regional assets, reusable asset classifications, measurement APIs, KPI queries, deterministic producer simulation, reusable time-series aggregation and persisted simulation-run tracking.

## Current Version

**`v0.11.0 – Simulation Foundation`**

Main additions:

- configurable simulation periods, intervals, modes and random seeds,
- deterministic point-in-time power simulation,
- producer profiles for solar, wind, hydro and biomass,
- a registry that connects asset types with profile, default asset and context factories,
- reusable interval aggregation with linear interpolation and trapezoidal energy integration,
- database-backed loading of supported simulation assets,
- persisted `simulation_runs` with `created`, `running`, `completed` and `failed` states,
- batch persistence of generated point-in-time power measurements,
- success, smoke and rollback integration tests against PostgreSQL.

## Project Goal

The project demonstrates practical backend and data engineering with visible energy-domain value:

- relational PostgreSQL modeling,
- typed REST APIs with FastAPI and Pydantic,
- database-backed read and write operations,
- deterministic simulation and analytics logic,
- automated unit, API, repository, service and integration testing,
- reproducible local startup with Docker Compose,
- later demand simulation, storage behavior, weather influence, energy balance and recommendations.

## Architecture

```text
Client / Swagger UI
        |
        v
FastAPI + Pydantic
        |
        v
Existing database / KPI access
        |
        v
PostgreSQL
  ├── regions
  ├── asset_types
  ├── assets
  ├── simulation_runs
  ├── measurements
  └── storage_specs

Internal simulation flow
------------------------
PostgreSQL assets
        |
        v
simulation.repository + simulation.mapper
        |
        v
SimulationAsset
        |
        v
profile registry + simulation engine
        |
        v
PowerMeasurement                 <- persisted raw simulation output
        |
        +-----------------------> measurements
        |
        v
measurement_aggregation
        |
        v
PowerIntervalDraft               <- derived in memory, not persisted
```

## Simulation Model

`v0.11.0` introduces a producer-focused simulation foundation.

Supported asset types:

- `solar_park`
- `wind_park`
- `hydro_power_plant`
- `biomass_power_plant`

A simulation run uses `SimulationConfig` with:

```text
start_time
end_time
interval_minutes
random_seed
simulation_mode
```

Supported interval sizes are `5`, `15`, `30` and `60` minutes. Supported modes are `historical`, `live`, `forecast` and `scenario`; the current default and implemented demo flow use `historical`.

The time grid stores **power support points**, not interval-energy rows. For example:

```text
2 hours / 15 minutes
→ 8 complete intervals
→ 9 power grid points per asset
```

Incomplete remainder time after the last complete interval is ignored.

### Producer profiles

- **Solar:** triangular daylight profile between default sunrise `06:30`, peak `12:30` and sunset `18:30`.
- **Wind:** seeded random variation around a default factor of `0.85`.
- **Hydro:** stable default factor of `0.90`.
- **Biomass:** stable default factor of `0.85`.
- Non-online assets currently return `0.0 kW`.
- Generated power is validated to remain between `0` and the asset rated power.

## Measurement Aggregation

The generic aggregation module converts point-in-time power measurements into derived intervals without persisting the result.

```text
PowerMeasurement
        |
        v
select interval source measurements
        |
        v
create measured/interpolated support points
        |
        v
build adjacent PowerSegments
        |
        v
trapezoidal energy integration
        |
        v
PowerIntervalDraft
```

A derived interval contains:

- interval start and end,
- time-weighted average active power,
- derived `energy_kwh`,
- coverage ratio,
- interval quality status,
- source and usable measurement counts,
- aggregation method metadata.

`source_measurement_count` counts only raw measurements relevant to that specific interval. Interpolated support points are derived values and are not counted as source measurements.

## Important `v0.11.0` Measurement Transition

The project is deliberately in a short transition between the older interval-based measurement contract and the new point-in-time raw measurement model.

Existing seed/API-created rows may still contain:

```text
interval_minutes
energy_kwh
```

New runtime simulation rows persist only raw power data and therefore use:

```text
interval_minutes = NULL
energy_kwh = NULL
```

Read responses accept these nullable values so simulated measurements can be retrieved through the existing API.

The full cleanup is intentionally deferred to **`v0.11.1 – Point-in-Time Measurement Refactor`**, where interval and energy fields will be removed from raw measurement persistence and energy/KPI logic will be derived from power measurements through aggregation.

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

List endpoints use compact summary contracts. Detail, POST and PATCH endpoints use the complete measurement contract.

For `v0.11.0`, measurement read responses allow `interval_minutes` and `energy_kwh` to be `null`. `POST /measurements` still uses the previous interval-based create contract and therefore requires both values.

### KPIs

- `GET /kpis/measurements`
- `GET /assets/{asset_id}/kpis`

The existing KPI implementation remains based on the pre-`v0.11` interval-energy model and valid-only SQL aggregation. The planned `v0.11.1` refactor will align KPI energy calculation with point-in-time raw measurements.

### Simulation API

There is **no public simulation REST endpoint in `v0.11.0`**. Simulation is executed through the internal service layer and the developer demo script. A public simulation API is planned only after the measurement-model refactor.

## Technology Stack

| Area | Technologies |
|---|---|
| Backend | Python 3.14, FastAPI, Pydantic, OpenAPI |
| Database | PostgreSQL 18, psycopg 3 |
| Simulation | dataclasses, seeded `Random`, profile registry, time-grid generation |
| Aggregation | interpolation, time-weighted average power, trapezoidal integration |
| Testing | pytest, FastAPI TestClient, dedicated test database |
| Quality | Ruff, pytest markers, deterministic seeds and rollback tests |
| Deployment | Docker, Docker Compose, PostgreSQL health check, named volume |
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

Install development dependencies and run the complete test suite:

```bash
py -m pip install -r requirements-dev.txt
py -m pytest -v
py -m ruff check src tests scripts
```

Run the simulation smoke/integration path:

```bash
py -m pytest -m smoke -v
```

Run the manual simulation service demo:

```bash
py -m scripts.run_simulation_demo
```

> The demo writes simulation runs and measurements to the configured application database.

Recreate the Docker development database after schema changes:

```bash
docker compose down -v
docker compose up --build -d
```

> This deletes the persistent development database volume.

## Database Model

| Table | Purpose |
|---|---|
| `regions` | Schematic model regions such as `DE-NORTH` |
| `asset_types` | Reusable roles and technical capability flags |
| `assets` | Producer, consumer, storage and grid master data |
| `simulation_runs` | Configuration, lifecycle timestamps, status and generated measurement count for persisted runs |
| `measurements` | Measurement time series; runtime simulation rows are point-in-time active-power measurements |
| `storage_specs` | Static battery-storage specifications |

Development seeds contain four German model regions, 13 reusable asset types and 16 assets. Deterministic test seeds provide valid, invalid, estimated and empty-data scenarios.

## Testing

The current source defines **101 test functions**. Parameterization expands them to **128 collected test cases** in this source state.

Coverage includes:

- general API endpoints,
- asset summary/detail behavior,
- measurement reads, POST and PATCH,
- validation and not-found behavior,
- global and asset-specific KPIs,
- time-grid behavior,
- solar, wind, hydro and biomass profiles,
- deterministic seed behavior,
- multi-asset simulation,
- measurement interpolation and interval aggregation,
- simulation mappers, repository and service orchestration,
- real PostgreSQL success/smoke integration,
- real PostgreSQL rollback behavior after a duplicate measurement conflict.

## Documentation

| Document | Purpose |
|---|---|
| [`docs/api_reference.md`](docs/api_reference.md) | Public endpoint and response contracts |
| [`docs/data_dictionary.md`](docs/data_dictionary.md) | Database, API, simulation and aggregation field definitions |
| [`docs/database_notes.md`](docs/database_notes.md) | Schema, repository/service persistence and transaction behavior |
| [`docs/test_strategy.md`](docs/test_strategy.md) | Test database, fixtures, markers and simulation test strategy |
| [`docs/deployment_notes.md`](docs/deployment_notes.md) | Docker, environment and local simulation demo |
| [`docs/version_history.md`](docs/version_history.md) | Project milestones and next planned patches |

## Repository Structure

```text
energy-operations-platform/
├── docs/
├── scripts/
│   └── run_simulation_demo.py
├── sql/
├── src/
│   ├── measurements/
│   │   ├── measurement_aggregation.py
│   │   └── models.py
│   └── simulation/
│       ├── default_data.py
│       ├── engine.py
│       ├── mapper.py
│       ├── models.py
│       ├── profiles.py
│       ├── registry.py
│       ├── repository.py
│       ├── schemas.py
│       ├── service.py
│       ├── simulation.py
│       └── time_grid.py
├── tests/
│   ├── integration/
│   └── unit/
├── compose.yaml
├── Dockerfile
├── pytest.ini
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── run_api.py
└── README.md
```

Private notes, logs, environments, `.env` files, bytecode and archives are excluded from Git and the Docker build context.

## Roadmap

1. **`v0.11.1` – Point-in-Time Measurement Refactor**: remove interval/energy fields from raw measurement persistence and align API/KPI logic with derived interval aggregation.
2. Public simulation API after the raw measurement contract is stable.
3. Consumer/load profiles and broader multi-asset simulation.
4. Storage state and dispatch behavior.
5. Regional weather simulation and weather-driven generation.
6. Global and regional energy balance.
7. Rule-based operational recommendations.
8. React dashboard with map, charts and live/history views.
9. Azure deployment after the backend MVP is stable.

## Portfolio Positioning

The project is designed as more than a generic CRUD API. It combines backend engineering, relational modeling, simulation, time-series processing, transactional persistence, automated quality controls and reproducible infrastructure with an energy-domain model that can grow into a realistic operational platform.
