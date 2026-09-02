# Energy Operations Platform

## Overview

The **Energy Operations Platform** is a backend and data portfolio project for modeling, validating, simulating, analyzing and exposing operational energy data.

It combines PostgreSQL, FastAPI, Pydantic, pytest and Docker Compose with a domain model for technical energy assets. The current backend supports regional assets, point-in-time power measurements, deterministic producer and consumer simulation, reusable time-series aggregation, period-based KPIs and persisted simulation-run tracking.

## Current Version

**`v0.12.0 – Consumer Load Simulation`**

Main additions:

- added `city_load` and `industrial_load` consumer profiles,
- modeled daily consumer demand with piecewise-linear load-factor interpolation,
- reused the existing simulation engine and profile registry for producers and consumers,
- kept consumer `active_power_kw` positive; `asset_role` will determine production/consumption semantics in the later balance layer,
- added default consumer assets and simulation contexts with configurable `load_factor`,
- extended mixed-asset simulation and PostgreSQL integration coverage to include both consumer types,
- retained the canonical point-in-time measurement model and period-based KPI derivation introduced in `v0.11.1`.

## Project Goal

The project demonstrates practical backend and data engineering with visible energy-domain value:

- relational PostgreSQL modeling,
- typed REST APIs with FastAPI and Pydantic,
- database-backed read and write operations,
- deterministic simulation and analytics logic,
- automated unit, API, repository, service and integration testing,
- reproducible local startup with Docker Compose,
- energy-balance analytics and a frontend-ready API as the next backend steps, followed by a React/TypeScript dashboard; storage, weather, recommendations and cloud deployment remain post-MVP work.

## Architecture

```text
Client / Swagger UI
        |
        v
FastAPI + Pydantic
        |
        +--------------------------+
        |                          |
        v                          v
Measurement CRUD             KPI endpoints
        |                          |
        v                          v
PostgreSQL measurements   period-aware DB retrieval
                                   |
                                   v
                           measurement service
                                   |
                                   v
                         interval aggregation
                                   |
                                   v
                    avg power / energy / coverage

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

`v0.12.0` extends the existing simulation foundation with consumer load profiles while keeping one shared engine and registry.

Supported runtime asset types:

- `solar_park`
- `wind_park`
- `hydro_power_plant`
- `biomass_power_plant`
- `city_load`
- `industrial_load`

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

### Consumer profiles

- **City load:** piecewise-linear daily profile with low night demand, morning rise, daytime demand and a clear evening peak.
- **Industrial load:** piecewise-linear daily profile with night base load, production ramp-up, a high daytime plateau and an evening drop.
- Consumer power is calculated as `rated_power_kw × profile_factor × context.load_factor`.
- Consumer `active_power_kw` remains non-negative; role-aware subtraction is intentionally deferred to the Energy Balance layer.
- The same generic engine validates producer and consumer output against `0 <= active_power_kw <= rated_power_kw`.

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

## Canonical Point-in-Time Measurement Model

Since `v0.11.1`, one row in `measurements` represents a **point-in-time active-power value**:

```text
measurement_id
asset_id
simulation_run_id
measurement_time
active_power_kw
source
quality_status
created_at
```

The database no longer stores `interval_minutes` or `energy_kwh` on raw measurement rows. Energy is derived for a requested period from the stored power time series, so the same raw data can later be analyzed using different interval sizes.

`simulation_runs.interval_minutes` remains part of the run configuration because it describes the generated simulation grid, not an individual raw measurement.

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

Measurement create/read contracts now use the same point-in-time model and no longer expose raw `interval_minutes` or stored `energy_kwh` fields.

### KPIs

- `GET /kpis/measurements?start_time=...&end_time=...`
- `GET /assets/{asset_id}/kpis?start_time=...&end_time=...`

KPI energy is derived on demand from the requested power time series. Boundary support measurements may be used for interpolation, while measured count/min/max values remain scoped to real valid measurements inside the requested period.

### Simulation API

There is **no public simulation REST endpoint in `v0.12.0`**. Simulation is executed through the internal service layer and developer demo script.

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
| `measurements` | Canonical point-in-time active-power time series |
| `storage_specs` | Static battery-storage specifications |

Development/test seed data now follows the point-in-time measurement model. Derived energy is calculated through the measurement aggregation/KPI layer rather than stored on measurement rows.

## Testing

The test suite covers the domain-heavy and critical integration paths, including:

- general asset and measurement API behavior,
- point-in-time measurement create/read/update flows,
- period-based global and asset KPIs,
- boundary support selection and interpolation,
- time-weighted average power and trapezoidal energy integration,
- coverage and quality handling,
- deterministic producer and consumer simulation,
- mixed producer/consumer simulation through the shared registry and engine,
- simulation repository/service orchestration,
- PostgreSQL success/smoke and rollback behavior.

For this learning project, testing follows an 80/20 approach: complex domain logic and critical persistence flows receive detailed coverage, while repeated framework-standard validation cases are kept intentionally limited.

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

1. Energy Balance: combine producer and consumer power/energy into production, consumption and net balance.
2. Frontend-ready backend: balance series, dashboard contracts and CORS, followed by backend feature freeze.
3. React + TypeScript + Vite dashboard with KPI cards, balance chart and asset overview.
4. Full-stack portfolio polish, architecture diagram, screenshots and `v1.0.0`.
5. Post-MVP: weather-driven generation, storage/SoC, recommendations, monitoring and Azure deployment.

Large structural refactors remain secondary unless they solve a concrete development problem.

## Portfolio Positioning

The project is designed as more than a generic CRUD API. It combines backend engineering, relational modeling, simulation, time-series processing, transactional persistence, automated quality controls and reproducible infrastructure with an energy-domain model that can grow into a realistic operational platform.
