# Version History

This document tracks the main implementation and learning milestones of the Energy Operations Platform.

The project uses small, explainable versions so the GitHub history shows how the platform evolved from Python fundamentals into a domain-oriented backend with simulation and time-series processing.

## Current Version

| Version | Status | Summary |
|---|---|---|
| `v0.11.0` | current | Simulation foundation with producer profiles, raw power persistence, interval aggregation, simulation-run tracking and real PostgreSQL success/rollback integration tests |

## Version Timeline

| Version | Status | Main result | Learning value |
|---|---|---|---|
| `v0.1` | completed | Python dictionaries, first statistics and classification logic | Python syntax, functions and data structures |
| `v0.2` | completed | File handling, TXT/CSV workflows and error handling | File processing and robust data flow |
| `v0.3` | completed | `Asset` class and CSV-to-object workflow | OOP, encapsulation and modules |
| `v0.3.2` | completed | Logging, README and first GitHub-ready structure | Traceability and documentation |
| `v0.4` | completed | PostgreSQL schema, seed data, queries and Python DB access | Relational modeling and DB integration |
| `v0.4.1` | completed | Tuple-to-dictionary database result mapping | JSON and API preparation |
| `v0.5` | completed | First FastAPI app with general, asset and measurement reads | Backend, HTTP and JSON basics |
| `v0.5.1` | completed | Swagger/OpenAPI metadata | API discoverability |
| `v0.5.2` | completed | Pydantic response models | Typed API contracts |
| `v0.5.3` | completed | First pytest/TestClient tests | Automated API testing |
| `v0.6.0` | completed | `POST /measurements` | Insert flow and write API |
| `v0.6.1` | completed | Measurement input validation | Pydantic constraints and 422 behavior |
| `v0.6.2` | completed | Measurement detail endpoint and create/read flow | Resource detail and persistence tests |
| `v0.6.3` | completed | PATCH for measurement quality status | Partial updates and data quality |
| `v0.7.0` | completed | Global measurement KPIs | SQL aggregation and valid-only analytics |
| `v0.7.1` | completed | Asset-specific KPIs | Scoped analytics and empty results |
| `v0.8.0` | completed | Dedicated test database | Environment isolation |
| `v0.8.1` | completed | Deterministic KPI assertions | Stable exact-value tests |
| `v0.8.2` | completed | Improved POST/PATCH test flows | Maintainable write tests |
| `v0.8.3` | completed | pytest markers | Targeted test execution |
| `v0.8.4` | completed | Modular test files and shared fixtures | Test organization |
| `v0.8.5` | completed | Test strategy and documentation split | Clear user/developer documentation |
| `v0.8.6` | completed | Centralized 404 helpers | Reduced API duplication |
| `v0.8` | released | Testing, robustness and API consistency milestone | First portfolio-oriented pre-release |
| `v0.9.0` | completed | Dockerfile and standalone FastAPI image | Container basics and port mapping |
| `v0.9.1` | completed | Compose stack for FastAPI and PostgreSQL | Multi-container networking, volumes and initialization |
| `v0.9.2` | completed | PostgreSQL health check and delayed API startup | Reliable service readiness |
| `v0.10.0` | completed | Energy-domain database, API and test migration | Domain modeling, schema evolution, API contracts and energy analytics |
| `v0.11.0` | current | Deterministic producer simulation, point-in-time persistence, interval aggregation and run lifecycle | Simulation architecture, seeded randomness, time-series integration, repositories/services and transactional failure handling |

---

# v0.8 Focus — Testing and Robustness

The `v0.8` milestone established:

- an isolated test database,
- deterministic seed scenarios,
- exact KPI assertions,
- POST/PATCH persistence flows,
- pytest markers,
- modular test files,
- shared fixtures,
- centralized 404 handling,
- clearer documentation boundaries.

---

# v0.9 Focus — Docker Foundation

The `v0.9.x` series added:

- a FastAPI Docker image,
- a clean build context,
- FastAPI and PostgreSQL Compose services,
- internal hostname `db`,
- persistent database storage,
- automatic first-run schema and seed initialization,
- PostgreSQL health checking,
- API startup after database readiness.

The infrastructure foundation is sufficient for current local backend development. Further Docker work follows real deployment needs rather than adding tooling for its own sake.

---

# v0.10.0 — Energy Domain Foundation

## Database and domain model

- replaced the narrow station concept with `assets`,
- added four schematic German regions,
- added reusable `asset_types`,
- introduced producer, consumer, storage and grid roles,
- added renewable, weather-dependent, dispatchable and storage capability flags,
- expanded asset master data with codes, location, rated power, coordinates and operating status,
- replaced generic load/unit fields with active-power and energy terminology,
- added one-to-one battery `storage_specs`,
- added realistic development and deterministic test datasets.

## API contracts

- migrated routes and helpers from stations to assets,
- added compact `AssetSummaryResponse` and `MeasurementSummaryResponse`,
- retained rich detail responses for individual resources,
- unified GET detail, POST and PATCH measurement output,
- exposed public `asset_type` consistently while keeping `asset_type_name` internal to PostgreSQL.

## Analytics

- renamed load KPIs to active-power KPIs,
- added `total_energy_kwh`,
- retained valid-only analytics,
- tested exclusion of invalid and estimated measurements,
- preserved empty-KPI behavior for assets without valid rows.

---

# v0.11.0 — Simulation Foundation

## Simulation configuration and domain models

Added immutable `SimulationConfig` with:

```text
start_time
end_time
interval_minutes
random_seed
simulation_mode
```

It provides calculated duration, complete interval count, grid point count and effective end time.

Added internal:

```text
SimulationAsset
SimulationContext
SimulationState
```

The simulation engine works on these internal models rather than API schemas or raw database tuples.

## Time grid

Introduced fixed-step power grids with explicit complete-interval semantics:

```text
N complete intervals
→ N + 1 point-in-time power measurements
```

Non-aligned remainder time after the last complete interval is ignored.

## Producer profile registry

Added `SIMULATION_PROFILE_REGISTRY` with one `SimulationProfileDefinition` per supported asset type.

Each definition bundles:

```text
power_profile
default_asset_factory
context_factory
```

Supported runtime profiles:

- `solar_park`
- `wind_park`
- `hydro_power_plant`
- `biomass_power_plant`

Profile behavior:

- solar daylight curve,
- seeded wind variation,
- stable hydro factor,
- stable biomass factor,
- non-online assets produce zero,
- output is validated against rated power and negative values.

## Reusable measurement aggregation

Added a separate `src/measurements` domain layer with:

```text
PowerMeasurement
PowerSupportPoint
PowerSegment
PowerIntervalDraft
```

Aggregation supports:

- unsorted input,
- left/internal/right measurement selection,
- boundary interpolation,
- adjacent segment construction,
- trapezoidal energy integration,
- time-weighted average active power,
- coverage calculation,
- quality classification,
- invalid source-measurement filtering,
- per-interval source and valid measurement counts.

`PowerIntervalDraft` is derived in memory and is not persisted in `v0.11.0`.

## Simulation repository / mapper / service

Added dedicated simulation modules for:

- loading only registry-supported database assets,
- mapping database rows into simulation-domain objects,
- creating and reading simulation runs,
- status transitions,
- batch persistence of generated point-in-time power measurements,
- orchestration of simulation, persistence, aggregation and validation.

## Simulation-run database tracking

Added `simulation_runs` with:

```text
created
running
completed
failed
```

lifecycle states, configuration metadata, timestamps and generated measurement count.

Added optional:

```text
measurements.simulation_run_id
```

with `ON DELETE SET NULL`.

## Point-in-time runtime persistence

New simulation executions persist raw point-in-time power measurements:

```text
measurement_time
active_power_kw
source = simulation
quality_status = valid
simulation_run_id
```

The compatibility columns:

```text
interval_minutes
energy_kwh
```

remain `NULL` for these runtime-generated rows.

Read API schemas were made nullable for these fields so generated rows remain retrievable through the existing measurement API.

## Transaction and rollback behavior

A run record is committed before the generated-measurement transaction so a later failure can still be recorded.

Failure behavior:

```text
rollback generated work
→ mark run failed
→ commit failed status
→ re-raise original database/application exception
```

A real PostgreSQL integration test runs the same deterministic simulation twice. The second run triggers the unique asset/timestamp constraint and verifies that:

- the failed run remains traceable,
- zero measurements belong to it,
- no partial insert survives rollback.

## Test expansion

The current source contains:

```text
101 test functions
128 collected cases after literal parameterization
```

New coverage includes:

- simulation configuration,
- time-grid semantics,
- all four producer profiles,
- deterministic seed behavior,
- registry-based generic simulation,
- multi-asset simulation,
- interpolation and interval aggregation,
- simulation validation,
- mapper/repository/service tests,
- real PostgreSQL success/smoke path,
- real PostgreSQL rollback/failure path.

## Known transition intentionally left for the next patch

`v0.11.0` does **not** complete the full raw-measurement migration.

Existing seed/API-created measurements still use interval/energy fields, and KPI SQL still reflects that model. This is deliberately isolated into the next patch rather than expanding the simulation release further.

---

# Documentation Split

| Document | Role |
|---|---|
| `README.md` | concise portfolio entry point and quick start |
| `docs/api_reference.md` | public endpoint and model contracts |
| `docs/data_dictionary.md` | authoritative DB/API/simulation field definitions |
| `docs/database_notes.md` | schema, persistence and transaction implementation |
| `docs/test_strategy.md` | test database, fixtures, markers and scenarios |
| `docs/deployment_notes.md` | Docker, environment and local demo |
| `docs/version_history.md` | implementation and learning milestones |

---

# Next Planned Work

| Planned version/block | Focus |
|---|---|
| `v0.11.1` | point-in-time raw measurement refactor; remove interval/energy persistence coupling and align API/KPI energy derivation |
| later simulation patch | public simulation endpoint after the measurement contract is stable |
| producer/consumer expansion | load profiles and broader asset coverage |
| storage block | state of charge and dispatch behavior |
| weather block | regional weather time series and weather-driven generation |
| analytics block | global and regional energy balance |
| recommendation block | rule-based operational actions |
| frontend phase | React dashboard with map, KPIs, charts and live/history views |
| cloud phase | Azure deployment after the backend MVP is stable |
