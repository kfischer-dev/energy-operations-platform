# Version History

This document tracks the main implementation and learning milestones of the Energy Operations Platform.

The project uses small, explainable versions so the GitHub history shows how the platform evolved from Python fundamentals into a domain-oriented backend with simulation and time-series processing.

## Current Version

| Version | Status | Summary |
|---|---|---|
| `v0.11.1` | completed | Canonical point-in-time measurement model with period-based KPI derivation from raw power measurements |
| `v0.12.0` | current | Consumer load simulation with `city_load` and `industrial_load` on the shared simulation engine |

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
| `v0.11.0` | completed | Deterministic producer simulation, point-in-time persistence, interval aggregation and run lifecycle | Simulation architecture, seeded randomness, time-series integration, repositories/services and transactional failure handling |
| `v0.11.1` | completed | Canonical point-in-time measurements and period-based KPI derivation | Time-series modeling, boundary-aware SQL, interpolation and trapezoidal integration |
| `v0.12.0` | current | City and industrial consumer load profiles integrated into the existing simulation engine and persistence flow | Load-profile modeling, interpolation, mixed producer/consumer simulation and registry reuse |

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

# v0.11.1 — Point-in-Time Measurement Refactor

## Canonical measurement model

Removed the former raw-measurement fields:

```text
interval_minutes
energy_kwh
```

A measurement row now represents active power at one timestamp. API-created and simulation-created measurements use the same contract.

## Period-based KPI endpoints

Both global and asset KPI endpoints now require:

```text
start_time
end_time
```

Measured count/min/max are based on valid measurements inside the period. Average power, energy and coverage are derived from the reconstructed power curve.

## Derived energy and boundary handling

Energy is calculated on demand through:

```text
point-in-time power measurements
→ nearest boundary supports when needed
→ linear boundary interpolation
→ adjacent segments
→ trapezoidal integration
```

Support/interpolated values can influence derived average power, energy and coverage but do not change measured count/min/max.

## Global KPI source query

The global KPI database query was changed from loading the complete valid history to a bounded query using `start_time` and `end_time`.

It selects:

- valid measurements inside the requested period,
- nearest left/right support measurements per asset where required,
- no duplicate support row when an exact boundary measurement already exists.

This introduced practical use of PostgreSQL `DISTINCT ON`, exact-boundary checks and `NOT EXISTS` logic.

## Quality policy

Current KPI calculations use only `quality_status = valid`. Invalid and estimated measurements are excluded from KPI source data.

## Testing / learning focus

Tests were updated for the new measurement and KPI contracts, with detailed coverage concentrated on time-series behavior, boundary selection, energy integration and critical database/service flows. Future feature work follows an 80/20 testing approach so the learning project remains implementation-focused.

---

# v0.12.0 — Consumer Load Simulation

## Consumer profiles

Added two runtime consumer asset types to the existing simulation registry:

```text
city_load
industrial_load
```

`city_load` models low night demand, a morning rise, daytime demand and a clear evening peak. `industrial_load` models night base load, production ramp-up, a high daytime plateau and an evening decline.

Both use piecewise-linear interpolation between daily load-factor support points.

## Shared simulation engine

No separate consumer engine was introduced. Producer and consumer assets use the same:

```text
SimulationAsset
SimulationContext
SIMULATION_PROFILE_REGISTRY
simulate_asset_power_grid()
simulate_assets_power_grid()
```

Consumer power is calculated as:

```text
rated_power_kw × profile_factor × context.load_factor
```

Raw `active_power_kw` remains positive for consumers. `asset_role = consumer` will determine subtraction later in the Energy Balance layer.

## Default data and registry

Added default city/industrial assets and contexts, then registered both consumer types through `SimulationProfileDefinition` with their power-profile, asset-factory and context-factory functions.

## Mixed producer/consumer verification

Unit and integration coverage now verifies:

- consumer load-factor interpolation,
- representative city and industrial load behavior,
- `load_factor` scaling,
- mixed producer/consumer simulation through the generic engine,
- loading `city_load` and `industrial_load` from the test database,
- `asset_role = consumer`,
- persistence of both consumer types within a completed simulation run.

No database schema or public REST endpoint was added for this release.

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

| Planned block | Focus |
|---|---|
| energy-balance block (`v0.13`) | combine producer and consumer power/energy into production, consumption and net balance; add summary and series outputs |
| frontend-ready backend (`v0.14`) | CORS and only the API contracts required by the dashboard, then backend feature freeze |
| frontend phase (`v0.15`–`v0.17`) | React/TypeScript/Vite dashboard, API integration, charts, asset overview and portfolio polish |
| `v1.0.0` | first complete Full-Stack portfolio MVP with demo, screenshots, architecture diagram and setup |
| post-MVP | weather, storage/SoC, recommendations, monitoring and Azure/cloud deployment |

Large structural cleanup remains secondary unless it solves a concrete project problem.

