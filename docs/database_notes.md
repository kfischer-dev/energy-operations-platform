# Database Notes

## Purpose

This document describes the PostgreSQL implementation, Python database access and simulation persistence behavior of the Energy Operations Platform in `v0.11.0`.

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
- nullable positive `interval_minutes`,
- nullable non-negative `energy_kwh`,
- quality in `valid`, `invalid`, `estimated`,
- unique `(asset_id, measurement_time)`.

The unique asset/timestamp rule is deliberately used by the rollback integration test: running the same simulation twice over the same timestamps causes PostgreSQL `UniqueViolation` and exercises the real transaction failure path.

## Storage specifications

`asset_id` is both primary key and FK, creating a one-to-one relationship. Capacity/power values must be positive, efficiencies must be in `(0,100]`, and minimum state of charge must be lower than maximum.

---

# `v0.11.0` Measurement Transition

The table name `measurements` now serves two temporarily coexisting contracts.

## Seed/API interval rows

Existing deterministic seeds and `POST /measurements` still use:

```text
measurement_time
interval_minutes
active_power_kw
energy_kwh
```

## Runtime simulation rows

The new simulation service inserts:

```text
asset_id
simulation_run_id
measurement_time
active_power_kw
source
quality_status
```

and leaves:

```text
interval_minutes = NULL
energy_kwh = NULL
```

This is deliberate. Runtime simulation measurements are point-in-time power support values. Interval average power and energy are derived in memory by `src/measurements/measurement_aggregation.py`.

The mixed schema is a temporary compatibility measure for `v0.11.0`. The canonical point-in-time migration is planned for `v0.11.1`.

---

# Development Seed

`sql/seed_data.sql` creates:

- four model regions,
- 13 asset types,
- 16 assets,
- one completed historical `simulation_run`,
- 64 deterministic legacy interval-style measurements,
- one battery storage specification.

The seeded simulation run uses:

```text
simulation_mode = historical
interval_minutes = 15
random_seed = 42
status = completed
generated_measurement_count = 64
```

These seed rows predate the runtime point-in-time persistence path and intentionally retain interval/energy values until the next refactor.

---

# Test Seed

`sql/test_seed_data.sql` is deterministic and starts with:

```sql
TRUNCATE TABLE
    storage_specs,
    measurements,
    simulation_runs,
    assets,
    asset_types,
    regions
RESTART IDENTITY CASCADE;
```

The test seed contains:

- four regions,
- eight asset types,
- nine assets,
- one completed historical seed run,
- 24 deterministic interval-style measurements,
- deliberate invalid and estimated rows,
- one asset without measurements,
- one storage specification.

The test suite points the application to:

```text
energy_operations_test
```

and includes a safety guard that refuses to reset another database name.

---

# Existing General Database Access

`src/database.py` contains the older application data-access layer for:

- database connection creation,
- asset summary/detail queries,
- measurement summary/detail queries,
- measurement create/update flows,
- KPI queries,
- row-to-dictionary mapping.

This file intentionally remains unchanged in `v0.11.0` except for compatibility with nullable interval/energy fields.

The current KPI queries still aggregate valid rows using:

```sql
COUNT(*)
AVG(active_power_kw)
MIN(active_power_kw)
MAX(active_power_kw)
SUM(energy_kwh)
MAX(measurement_time)
```

Because new runtime simulation rows use `energy_kwh = NULL`, the KPI layer is a known transition area. It is planned for the `v0.11.1` point-in-time measurement refactor rather than being partially patched in `v0.11.0`.

---

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

Derived intervals are **not database entities in `v0.11.0`**.

The service creates them after persisting raw power points:

```text
PowerMeasurement list
→ group by asset
→ aggregate fixed intervals
→ validate complete coverage
→ return PowerIntervalDraft list
```

Energy is calculated through trapezoidal integration. Boundary values can be linearly interpolated from surrounding raw measurements.

`source_measurement_count` counts the raw measurements relevant to the specific interval, not the complete input list.

---

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

Known intentional limitations at the `v0.11.0` boundary:

1. `measurements.interval_minutes` and `measurements.energy_kwh` still exist for compatibility.
2. `POST /measurements` still creates interval-style rows.
3. KPI energy SQL still reflects the previous interval model.
4. `UNIQUE (asset_id, measurement_time)` prevents storing multiple scenario/forecast rows for the same asset/timestamp.
5. No migration framework is used yet; schema changes currently require controlled rebuilds.
6. `src/database.py` remains a large legacy data-access module and may be split during later refactoring.

The first three points are specifically planned for `v0.11.1`.
