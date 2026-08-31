# Database Notes

## Purpose

This document describes the PostgreSQL implementation, Python database access and simulation persistence behavior of the Energy Operations Platform in `v0.11.1`.

Related documents:

- [`data_dictionary.md`](data_dictionary.md)
- [`api_reference.md`](api_reference.md)
- [`test_strategy.md`](test_strategy.md)
- [`deployment_notes.md`](deployment_notes.md)

---

# Current Schema

The schema contains six tables:

```text
regions
asset_types
assets
simulation_runs
measurements
storage_specs
```

Relationship overview:

```text
regions 1 ───────< assets >─────── 1 asset_types
                    |
                    | 1
                    v
                measurements >──── 0..1 simulation_runs
                    |
                    |
                    +---- optional run ownership

assets 1 ─────── 0..1 storage_specs
```

More precisely:

- one region can contain many assets,
- one asset type can classify many assets,
- one asset can have many measurements,
- one simulation run can own many generated measurements,
- `measurements.simulation_run_id` is nullable,
- deleting a simulation run sets the measurement FK to `NULL`,
- deleting an asset cascades to its measurements and storage specification.

---

# Schema Constraints

## Regions

Unique:

```text
region_code
region_prefix
region_name
```

## Asset types

Unique:

```text
asset_type_name
asset_prefix
```

Allowed roles:

```text
producer
consumer
storage
grid
```

## Assets

Key rules:

- unique `asset_code`,
- positive `rated_power_kw`,
- valid latitude/longitude ranges,
- status in `online`, `offline`, `maintenance`, `fault`,
- required FK to `regions`,
- required FK to `asset_types`.

## Simulation runs

Rules:

- `end_time > start_time`,
- `interval_minutes > 0`,
- `random_seed >= 0` when present,
- non-negative generated count,
- mode in `historical`, `live`, `forecast`, `scenario`,
- status in `created`, `running`, `completed`, `failed`.

## Measurements

Rules:

- required asset FK,
- optional simulation-run FK,
- required `measurement_time`,
- required `active_power_kw`,
- required source,
- quality in `valid`, `invalid`, `estimated`,
- unique `(asset_id, measurement_time)`.

Raw measurement rows no longer contain `interval_minutes` or persisted `energy_kwh`.

The unique asset/timestamp rule is still deliberately used by the rollback integration test: running the same simulation twice over the same timestamps causes PostgreSQL `UniqueViolation` and exercises the real transaction failure path.

## Storage specifications

`asset_id` is both primary key and FK, creating a one-to-one relationship. Capacity/power values must be positive, efficiencies must be in `(0,100]`, and minimum state of charge must be lower than maximum.

---

# `v0.11.1` Point-in-Time Measurement Model

`measurements` now has one canonical meaning: a row stores active power at a timestamp.

```text
asset_id
simulation_run_id
measurement_time
active_power_kw
source
quality_status
```

The following former measurement columns were removed:

```text
interval_minutes
energy_kwh
```

Energy is derived from the power time series through the reusable aggregation layer. `simulation_runs.interval_minutes` remains unchanged because it describes the simulation grid configuration rather than raw measurement semantics.

# Development Seed

`sql/seed_data.sql` creates the current energy-domain master data, one completed historical simulation run and deterministic point-in-time power measurements.

The seeded run retains its own `interval_minutes` configuration, while measurement rows themselves are interval-independent.

# Test Seed

`sql/test_seed_data.sql` remains deterministic and resets identities before loading known scenarios.

The test data includes:

- valid point-in-time power series,
- deliberate invalid and estimated rows,
- exact and non-exact KPI boundaries,
- assets with one or no usable measurements,
- one storage specification,
- one completed historical simulation run.

The suite points the application to `energy_operations_test` and keeps the existing safety guard that refuses to reset another database name.

# Existing General Database Access

`src/database.py` remains the application data-access layer for general asset/measurement CRUD and KPI source queries.

For `v0.11.1` it was aligned with the point-in-time model:

- measurement SELECT/INSERT mapping no longer includes interval or stored energy fields,
- `POST /measurements` writes only raw power data,
- asset KPI retrieval loads the requested period plus nearest support measurements,
- global KPI retrieval accepts `start_time` / `end_time` and returns only period-relevant measurements plus per-asset support points.

The global KPI query uses PostgreSQL `DISTINCT ON` to select nearest supports per asset and exact-boundary checks/`NOT EXISTS` logic to avoid adding a support row when the boundary itself is already measured.

Energy mathematics is intentionally kept out of SQL. Database code selects the necessary raw measurements; the measurement service/aggregation layer performs interpolation, time weighting and trapezoidal integration.

# Simulation Repository Layer

`src/simulation/repository.py` separates simulation-specific SQL from the simulation engine.

## `fetch_simulation_assets()`

Loads only asset types passed by the service. `load_simulation_assets()` supplies the currently registered profile types, so unsupported database assets are not passed to the engine.

Returned fields include:

```text
asset_id
asset_code
asset_role
asset_type
region_id
region_code
rated_power_kw
operating_status
is_renewable
is_weather_dependent
is_dispatchable
can_store_energy
```

Rows are mapped through `map_simulation_asset_row()` and then converted to `SimulationAsset` by `map_asset_to_simulation_asset()`.

## Simulation-run functions

Repository operations:

```text
create_simulation_run()
mark_simulation_run_running()
mark_simulation_run_completed()
mark_simulation_run_failed()
fetch_simulation_run_by_id()
```

No repository function opens a separate application connection. The service passes one connection through the run lifecycle.

## `insert_power_measurements()`

Persists runtime simulation values with one `executemany()` call.

Inserted columns:

```text
asset_id
simulation_run_id
measurement_time
active_power_kw
source
quality_status
```

Not inserted:

```text
interval_minutes
energy_kwh
```

They therefore remain `NULL` for generated point-in-time measurements.

The repository returns the number of inserted rows. That value becomes `simulation_runs.generated_measurement_count` when the run completes.

The repository does not commit per measurement.

---

# Simulation Service Transaction Strategy

`execute_simulation_run()` owns the high-level transaction flow.

## Success path

```text
1. create simulation_run with status=created
2. COMMIT
3. mark run running and set started_at
4. COMMIT
5. load supported assets
6. simulate point-in-time PowerMeasurements
7. batch insert generated measurements
8. derive PowerIntervalDrafts in memory
9. validate all derived intervals as complete
10. mark run completed and write generated_measurement_count
11. COMMIT
12. return derived intervals
```

The early commits are intentional: the run metadata must survive a later simulation/persistence rollback so a failed execution remains traceable.

## Failure path

```text
error during simulation / insert / aggregation / validation
→ ROLLBACK generated work
→ mark run failed
→ set completed_at
→ COMMIT failed status
→ log exception
→ re-raise original exception
```

The failure integration test proves that:

- the successful first run remains completed,
- a duplicate second run becomes failed,
- the failed run owns zero persisted measurements,
- the total measurement count does not increase after rollback.

---

# Simulation Run Mapping

`src/simulation/mapper.py` provides:

```text
map_simulation_asset_row()
map_asset_to_simulation_asset()
map_simulation_run_row()
```

This keeps raw row positions out of service and engine logic.

PostgreSQL numeric rated power is converted to Python `float` when creating `SimulationAsset`.

---

# Derived Interval Aggregation

Derived intervals remain non-persistent domain results.

The same aggregation layer is now used by period KPIs:

```text
point-in-time PowerMeasurements
→ choose in-period measurements + supports
→ interpolate missing boundaries
→ build adjacent PowerSegments
→ trapezoidal energy integration
→ time-weighted average power
→ coverage ratio
```

Measured period statistics remain separate from derived values:

- `measurement_count`, measured min and measured max use valid measurements inside the requested period,
- boundary supports/interpolated points affect only derived average power, energy and coverage.

Global KPIs group measurements by `asset_id` before aggregation so no segment is ever built between different assets.

# Database Initialization with Docker

For a new volume, Compose mounts:

```text
sql/schema.sql    → /docker-entrypoint-initdb.d/01-schema.sql
sql/seed_data.sql → /docker-entrypoint-initdb.d/02-seed.sql
```

These scripts run only when PostgreSQL initializes an empty data directory.

After schema/seed changes:

```bash
docker compose down -v
docker compose up --build -d
```

This deliberately deletes and recreates the development database volume.

---

# Current Database Limitations / Next Refactor

Known intentional limitations after `v0.11.1`:

1. `UNIQUE (asset_id, measurement_time)` prevents storing parallel forecast/scenario values for the same asset/timestamp.
2. No migration framework is used yet; schema changes currently require controlled clean rebuilds.
3. `src/database.py` is still a comparatively large legacy data-access module and can be split later if it becomes a concrete development blocker.
4. KPI support selection is designed for the current PostgreSQL model and data scale; further performance optimization should follow measured need rather than be added pre-emptively.

The next project focus returns to visible domain functionality, starting with consumer/load simulation rather than additional infrastructure refactoring.

