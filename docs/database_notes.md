# Database Notes

## Purpose

This document explains the PostgreSQL implementation and Python database access layer of the Energy Operations Platform in `v0.10.0`.

Field-level definitions are maintained in [`data_dictionary.md`](data_dictionary.md). API behavior is documented in [`api_reference.md`](api_reference.md).

## Current Schema

The current schema contains five related tables:

```text
regions
   └── assets ── asset_types
          ├── measurements
          └── storage_specs
```

| Table | Main responsibility |
|---|---|
| `regions` | Stable model-region identifiers and descriptions |
| `asset_types` | Reusable technical classification and capability flags |
| `assets` | Physical or modeled energy assets |
| `measurements` | Interval-based power and energy time series |
| `storage_specs` | Static one-to-one battery-storage specifications |

## Relationships

| Parent | Child | Cardinality | Foreign key behavior |
|---|---|---|---|
| `regions` | `assets` | one-to-many | each asset requires one region |
| `asset_types` | `assets` | one-to-many | each asset requires one type |
| `assets` | `measurements` | one-to-many | deleting an asset cascades to measurements |
| `assets` | `storage_specs` | one-to-zero-or-one | deleting an asset cascades to storage specs |

`storage_specs.asset_id` is both the primary key and foreign key. This enforces at most one specification row per asset.

## Important Constraints

### Stable unique identifiers

```text
regions.region_code
regions.region_prefix
regions.region_name
asset_types.asset_type_name
asset_types.asset_prefix
assets.asset_code
```

### Measurement uniqueness

```text
UNIQUE (asset_id, measurement_time)
```

This prevents duplicate timestamps for the same asset.

### Checked values

The schema validates:

- asset roles,
- asset operating status,
- measurement quality status,
- positive rated power and storage limits,
- coordinate ranges,
- interval length,
- non-negative energy,
- percentage ranges,
- minimum SoC below maximum SoC.

`active_power_kw` intentionally has no non-negative database constraint. The test dataset uses negative invalid rows, and a future directional power convention remains possible.

## SQL Files

| File | Purpose |
|---|---|
| `sql/schema.sql` | Creates all five tables and constraints |
| `sql/seed_data.sql` | Development data used for local exploration and first Docker initialization |
| `sql/test_seed_data.sql` | Deterministic data for automated tests |
| `sql/example_queries.sql` | Learning, inspection and analytics queries |

## Development Seed Data

`seed_data.sql` currently creates:

- four German model regions,
- reusable producer, consumer, storage and grid asset types,
- sixteen assets,
- sixty-four 15-minute measurement rows,
- one battery-storage specification.

The dataset includes wind, solar, hydro, gas and biomass generation, consumer loads, substations and battery storage. It is designed for development and portfolio demonstration, not as a claim of real grid data.

## Test Seed Data

`test_seed_data.sql` starts with:

```sql
TRUNCATE TABLE
    storage_specs,
    measurements,
    assets,
    asset_types,
    regions
RESTART IDENTITY CASCADE;
```

Stable IDs then create explicit scenarios:

| Asset ID | Scenario |
|---:|---|
| `1` | known wind-production values for exact KPIs |
| `4` | battery storage with one `storage_specs` row |
| `5` | two invalid negative values and one valid value |
| `7` | two valid values and one estimated value |
| `8` | substation measurement and write-test target |
| `9` | existing asset without measurements |

The test data intentionally uses stable timestamps and values so KPI assertions remain deterministic.

## Data Quality Rule

Current KPI queries include only:

```sql
WHERE quality_status = 'valid'
```

Consequences:

- valid rows contribute to count, power aggregates, energy sum and latest timestamp,
- invalid rows remain stored but are excluded,
- estimated rows remain stored but are excluded.

A later version may expose separate raw, validated and estimated analytics rather than using one valid-only rule everywhere.

## Database Connection

`src/database.py` loads these environment variables:

```text
DB_NAME
DB_USER
DB_PASSWORD
DB_HOST
DB_PORT
```

The function:

```python
get_connection()
```

returns a psycopg connection used by the API endpoints and test reset helpers.

## Read Functions

### Active API reads

| Function | Purpose |
|---|---|
| `fetch_asset_summaries()` | Compact data for `GET /assets` |
| `fetch_asset_by_id()` | Complete asset detail |
| `fetch_measurement_summaries()` | Compact data for `GET /measurements` |
| `fetch_measurement_summaries_by_asset_id()` | Compact measurements for one asset |
| `fetch_measurement_by_id()` | Complete measurement detail |
| `fetch_measurement_kpi_summary()` | Global valid-only KPIs |
| `fetch_asset_kpi_summary()` | Valid-only KPIs for one asset |

### Remaining broader loaders

The module also retains broader loaders used by earlier report/demo workflows:

```text
fetch_assets()
fetch_joined_measurements()
fetch_measurements_by_asset_id()
fetch_database_report_data()
```

They are not used by the current FastAPI endpoints. They can be removed later when legacy report workflows are formally retired.

## Summary and Detail Mapping

The API intentionally uses separate mapping functions:

```text
map_asset_summary_row()
map_asset_row()
map_measurement_summary_row()
map_measurement_row()
map_kpi_measurement_row()
```

This avoids oversized list responses while retaining rich detail responses.

### Public type naming

The joined database column is:

```text
asset_type_name
```

The mapping layer exposes it to the API as:

```text
asset_type
```

## Write Operations

### Create measurement

`create_measurement()` performs an `INSERT` and returns only the new `measurement_id`:

```text
INSERT
→ RETURNING measurement_id
→ COMMIT
```

The API then calls `fetch_measurement_by_id()` so POST returns the same complete contract as the detail endpoint.

### Update quality status

`update_measurement_quality_status()` updates only `quality_status` and returns the ID. The API reloads the complete row afterward.

This pattern avoids separate POST and PATCH response mappers.

## KPI Queries

Both global and asset-specific KPI queries calculate:

```text
COUNT(*)
ROUND(AVG(active_power_kw), 2)
MIN(active_power_kw)
MAX(active_power_kw)
SUM(energy_kwh)
MAX(measurement_time)
```

When an existing asset has no valid measurements, PostgreSQL returns:

- `COUNT(*) = 0`,
- other aggregates as `NULL`.

This maps directly to the Pydantic response with zero count and nullable KPI values.

## Test Database

Automated tests use:

```text
energy_operations_test
```

`tests/conftest.py` sets `DB_NAME` before importing the application and includes a safety guard that refuses to run the reset helper against a differently named database.

The reset helper executes only `sql/test_seed_data.sql`; the test database schema must already exist.

## Docker Initialization

Docker Compose mounts:

```text
sql/schema.sql    → /docker-entrypoint-initdb.d/01-schema.sql
sql/seed_data.sql → /docker-entrypoint-initdb.d/02-seed.sql
```

PostgreSQL executes these scripts only when the named volume is initialized for the first time.

After schema changes, recreate the development database deliberately:

```bash
docker compose down -v
docker compose up --build
```

## Current Limitations

- No migration framework; schema changes currently require manual rebuilds.
- No repository/service abstraction; SQL remains in `database.py`.
- Tuple mapping depends on SQL column order.
- Asset filtering and list limiting currently happen in Python rather than SQL.
- Measurement energy consistency is not enforced by a database formula.
- Storage specifications are not exposed through API endpoints yet.
- No transaction rollback fixture for per-test isolation.
- No database indexes beyond primary keys and unique constraints.

## Next Database Improvements

High-value next steps after the simulation foundation:

1. Add simulation-run metadata.
2. Add dynamic storage-state records.
3. Add weather time series by region.
4. Move filtering and limiting into parameterized SQL.
5. Introduce migrations before the first cloud deployment.
6. Review indexes using real query patterns.
