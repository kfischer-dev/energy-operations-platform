# Test Strategy

## Purpose

This document describes the automated test approach of the Energy Operations Platform in `v0.11.0`.

The current source defines **101 test functions**. Literal parameterization expands these to **128 collected test cases** in this source state.

The strategy combines:

- deterministic API tests,
- database-backed endpoint tests,
- pure simulation/profile logic tests,
- reusable measurement aggregation tests,
- mocked repository/service unit-style tests,
- real PostgreSQL integration, smoke and rollback tests.

---

# Test Structure

```text
tests/
├── conftest.py
├── test_general.py
├── integration/
│   └── test_repository_service.py
└── unit/
    ├── analytics/
    │   └── test_kpis.py
    ├── assets/
    │   └── test_assets.py
    ├── measurements/
    │   ├── test_measurement_aggregation.py
    │   └── test_measurements.py
    └── simulation/
        ├── test_engine.py
        ├── test_mappers.py
        ├── test_simulation.py
        ├── test_simulation_profiles.py
        ├── test_simulation_repository.py
        ├── test_simulation_service.py
        ├── test_simulation_time_grid.py
        └── test_simulation_validation.py
```

The `unit/` directory is currently an organizational grouping, not a guarantee that every contained test is infrastructure-free. API tests under that tree still use the real dedicated test database through `TestClient` and `src.database`.

The stricter DB/service end-to-end tests live under `tests/integration/`.

---

# Dedicated Test Database

Before importing the FastAPI application, `tests/conftest.py` sets:

```text
DB_NAME=energy_operations_test
```

Safety guard:

```python
if os.environ["DB_NAME"] != "energy_operations_test":
    raise RuntimeError("Refusing to reset non-test database")
```

This prevents the reset helper from intentionally targeting another database name.

## Session reset

An autouse session fixture executes `sql/test_seed_data.sql` before the test session.

```text
setup_test_database()
```

## Per-test exact reset

Tests requiring deterministic seed IDs/counts request:

```text
reset_db
```

The fixture reloads `sql/test_seed_data.sql` and commits the reset.

The test seed resets identity values and defines exact KPI, invalid, estimated and empty-data scenarios.

---

# Shared Fixtures

Main fixtures in `tests/conftest.py`:

| Fixture | Purpose |
|---|---|
| `database_connection` | Real connection to the dedicated test database |
| `reset_db` | Restore deterministic SQL seed data |
| `client` | FastAPI `TestClient` |
| `valid_measurement_payload` | Stable POST base payload |
| `daylight_factor_payload` | Sunrise/peak/sunset minutes |
| `engine_payload` | Parametrized config/asset/context/profile bundle |

`engine_payload` supports:

```text
solar_park
wind_park
hydro_power_plant
biomass_power_plant
```

---

# API and Domain Test Coverage

## General

- `GET /`
- `GET /health`

## Assets

Tests cover:

- summary list contract,
- exact filtering by `asset_type`,
- detail response,
- not-found behavior,
- invalid path IDs.

## Measurements

Tests cover:

- summary list behavior,
- limit query validation,
- asset-specific list behavior,
- detail read,
- `404` and `422` behavior,
- POST success and persistence,
- POST validation,
- PATCH success and persistence,
- PATCH validation,
- read compatibility with nullable `interval_minutes` / `energy_kwh` for runtime simulation rows.

`POST /measurements` still uses the previous interval-energy create contract in `v0.11.0`.

## KPIs

Tests cover exact valid-only:

```text
measurement_count
average_power_kw
min_power_kw
max_power_kw
total_energy_kwh
latest_measurement_time
```

They also verify:

- invalid rows are excluded,
- estimated rows are excluded,
- existing asset without valid measurements returns zero/null values,
- unknown asset returns `404`.

The KPI tests intentionally remain tied to the deterministic pre-refactor interval seed in `v0.11.0`. KPI semantics for new point-in-time simulation rows are planned for `v0.11.1`.

---

# Simulation Test Coverage

## Configuration and time grid

Tests cover:

- valid `SimulationConfig`,
- invalid time ordering,
- supported/unsupported intervals,
- supported/unsupported modes,
- non-negative seed validation,
- complete interval count,
- grid point count,
- effective end time,
- non-aligned end times,
- invalid time-grid arguments.

Key semantic rule:

```text
N complete intervals → N + 1 power grid points
```

## Producer profiles

### Solar

Coverage includes:

- before sunrise,
- sunrise,
- rising profile,
- peak,
- falling profile,
- sunset / after sunset,
- rated-power scaling,
- invalid sun-time order.

### Wind

Coverage includes:

- seeded reproducibility,
- different seeds change the sequence,
- expected variation range,
- external context factor behavior.

### Hydro / biomass

Tests verify deterministic scaling from configured context factors.

## Generic simulation behavior

Tests verify:

- profile registry lookup,
- default asset creation,
- context creation,
- unsupported types,
- offline/maintenance/fault output becomes zero,
- power cannot exceed rated power,
- power cannot be negative,
- one-asset power grid generation,
- multi-asset power grid generation,
- interval generation and multi-asset interval aggregation.

---

# Measurement Aggregation Test Coverage

`test_measurement_aggregation.py` covers the reusable time-series logic independently from PostgreSQL.

Key areas:

- linear boundary interpolation,
- interpolation input validation,
- chronological sorting without mutating source order,
- left/internal/right source selection,
- source measurement counting per interval,
- measured and interpolated support points,
- segment building,
- trapezoidal segment energy,
- total interval energy,
- covered duration,
- time-weighted average power,
- `valid`, `incomplete` and `invalid` coverage behavior,
- exclusion of invalid raw measurements from usable aggregation inputs,
- duplicate timestamp rejection,
- mixed asset-ID rejection,
- consecutive interval aggregation.

## Source count contract

`source_measurement_count` counts only raw measurements selected as relevant to the specific interval.

Example:

```text
10:00
10:15
10:30
```

For `10:00–10:15`:

```text
source_measurement_count = 2
valid_measurement_count = 2
```

A generated interpolated boundary point does not add to the source count.

---

# Mapper, Repository and Service Tests

## Mappers

Mapper tests verify:

- database asset dictionary → `SimulationAsset`,
- tuple row → simulation asset dictionary,
- tuple row → simulation-run dictionary,
- numeric rated power is converted appropriately for simulation use.

## Repository

Repository tests mock the connection/cursor contract to verify:

- one point-in-time measurement insert,
- multi-row `executemany()` behavior,
- correct measurement tuple values,
- empty list returns `0` without opening a cursor.

The simulation insert intentionally does not supply `interval_minutes` or `energy_kwh`.

## Service

Service tests mock external operations and verify orchestration:

```text
create run
→ running
→ simulate
→ insert measurements
→ aggregate
→ validate
→ completed
```

Failure-unit behavior verifies rollback and transition to failed when batch persistence raises an exception.

---

# PostgreSQL Integration Tests

`tests/integration/test_repository_service.py` contains the highest-value current integration paths.

## Supported asset loading

Verifies:

```text
PostgreSQL
→ registry-supported asset filter
→ repository row mapping
→ SimulationAsset objects
```

Unsupported types such as `battery_storage` are not loaded for the current producer engine.

## Smoke / success path

Markers:

```text
smoke
integration
```

The test executes a real simulation and verifies:

- a simulation run is persisted,
- the run ends in `completed`,
- generated count equals the actual number of persisted rows for the run,
- a generated measurement can be read back through FastAPI,
- `source = simulation`,
- `active_power_kw` is present,
- `interval_minutes = null`,
- `energy_kwh = null`,
- quality status is valid.

This is the critical `v0.11.0` cross-layer contract test.

## Real failure / rollback path

Markers:

```text
failure
integration
```

Flow:

```text
Run A over a deterministic period
→ completed
→ measurements persisted

Run B over the same asset timestamps
→ PostgreSQL UniqueViolation
→ service rollback
→ Run B marked failed
```

Assertions verify:

- Run A remains completed,
- Run B is failed,
- Run B generated count is zero,
- Run B owns zero measurement rows,
- total measurement count remains unchanged after the failed run.

---

# Pytest Markers

Configured in `pytest.ini`:

| Marker | Purpose |
|---|---|
| `post` | POST endpoint tests |
| `patch` | PATCH endpoint tests |
| `kpi` | KPI/analytics tests |
| `validation` | validation and invalid-input behavior |
| `time_grid` | time-grid tests |
| `sim_profiles` | simulation profile tests |
| `simulation` | simulation engine/functions |
| `aggregation` | measurement aggregation tests |
| `intermediate` | intermediate categorization |
| `unit` | explicitly marked unit tests |
| `integration` | real integration tests |
| `repository` | repository-focused tests |
| `service` | service-focused tests |
| `smoke` | primary success path |
| `failure` | expected application failure and rollback path |

Important: the `unit` marker is not currently attached to every file under `tests/unit/`. Use the folder path when you want the full organizational unit tree.

---

# Recommended Commands

Complete suite:

```bash
py -m pytest -v
```

Simulation-focused logic:

```bash
py -m pytest tests/unit/simulation -v
```

Aggregation:

```bash
py -m pytest tests/unit/measurements/test_measurement_aggregation.py -v
```

API measurement tests:

```bash
py -m pytest tests/unit/measurements/test_measurements.py -v
```

Integration:

```bash
py -m pytest -m integration -v
```

Smoke:

```bash
py -m pytest -m smoke -v
```

Rollback/failure:

```bash
py -m pytest -m failure -v
```

KPI:

```bash
py -m pytest -m kpi -v
```

POST / PATCH:

```bash
py -m pytest -m post -v
py -m pytest -m patch -v
```

Static quality check:

```bash
py -m ruff check src tests scripts
```

Syntax compilation:

```bash
py -m compileall src tests scripts
```

---

# Release Test Rule

Before tagging a release:

```text
1. reset/recreate the required database environment
2. run complete pytest suite
3. run Ruff
4. perform Docker clean rebuild when schema/seed changed
5. run smoke integration path
6. inspect git status and release diff
```

`v0.11.0` specifically requires the success smoke path and real PostgreSQL rollback path to remain green.

---

# Known Test-Architecture Improvement

A later cleanup can move database setup fixtures closer to integration/API tests so truly pure simulation and aggregation tests can run without any database-session initialization. That is a structural improvement, not a blocker for `v0.11.0`.
