# Database Notes

This document focuses on the PostgreSQL data model, SQL files and database access layer of the Energy Operations Platform.

For endpoint behavior, see [`api_reference.md`](api_reference.md).  
For test setup and test data handling, see [`test_strategy.md`](test_strategy.md).  
For version milestones, see [`version_history.md`](version_history.md).

## Purpose

The database layer stores station master data and measurement values for technical energy assets. It supports:

- station lookup,
- measurement lookup,
- measurement creation,
- measurement quality updates,
- global KPI calculations,
- station-specific KPI calculations.

## Why PostgreSQL?

The project moved from CSV files to PostgreSQL because the Energy Operations Platform needs:

- persistent structured data,
- clear relationships between stations and measurements,
- SQL joins and aggregations,
- data-quality fields such as `quality_status`,
- API endpoints backed by real database queries,
- a realistic foundation for Docker and later cloud deployment.

## Current Data Model

### `stations`

Stores energy station master data.

| Column | Purpose |
|---|---|
| `station_id` | Primary key |
| `station_name` | Human-readable station name |
| `station_type` | Asset type, for example `solar_park` or `wind_park` |
| `station_location` | Location name |

### `measurements`

Stores technical measurement values linked to stations.

| Column | Purpose |
|---|---|
| `measurement_id` | Primary key |
| `station_id` | Foreign key referencing `stations.station_id` |
| `measurement_time` | Timestamp of the measurement |
| `load_value` | Numeric load value |
| `unit` | Measurement unit, currently `kW` or `MW` at API level |
| `source` | Origin of the measurement, for example CSV import, Sensor API or SCADA |
| `quality_status` | Data-quality classification: `valid`, `invalid` or `estimated` |

## Key Relationship

```text
stations.station_id 1 ──── n measurements.station_id
```

A station can have many measurements. A measurement belongs to exactly one station.

## SQL Files

| File | Purpose |
|---|---|
| `sql/schema.sql` | Defines the core schema for stations and measurements |
| `sql/seed_data.sql` | Development/demo seed data |
| `sql/test_seed_data.sql` | Deterministic seed data for automated tests |
| `sql/example_queries.sql` | SQL learning queries for joins, filters and aggregations |

## Development Seed Data vs Test Seed Data

The project intentionally separates development data from deterministic test data.

| File | Used for | Stability expectation |
|---|---|---|
| `seed_data.sql` | local development and manual exploration | can evolve over time |
| `test_seed_data.sql` | automated tests and exact KPI assertions | should remain stable unless tests are updated together |

The test seed data contains specific scenarios:

- Station A has known valid measurements for station KPI checks.
- Station D contains invalid negative values plus one valid value for valid-only analytics checks.
- Station Z exists without measurements for empty KPI response checks.
- Station H contains high SCADA values and is used as an existing station for write-flow tests.

## Data Quality Rule

KPI endpoints currently include only valid measurements:

```sql
WHERE quality_status = 'valid'
```

This means invalid measurements remain stored in the database, but they do not influence KPI calculations.

## Current Database Access Layer

The database access functions are located in:

```text
src/database.py
```

Main function groups:

| Function group | Functions |
|---|---|
| Connection | `get_connection()` |
| Station reads | `fetch_stations()`, `fetch_station_by_id()` |
| Measurement reads | `fetch_joined_measurements()`, `fetch_measurements_by_station_id()`, `fetch_measurement_by_id()` |
| Measurement writes | `create_measurement()`, `update_measurement_quality_status()` |
| KPI reads | `fetch_measurement_kpi_summary()`, `fetch_station_kpi_summary()` |
| Mapping helpers | `map_station_row()`, `map_measurement_row()`, `map_detailed_measurement_row()`, `map_kpi_measurement_row()` |

## Query and Mapping Style

The current implementation uses:

- explicit SQL queries,
- parameterized SQL execution,
- dictionary mapping after `fetchone()` or `fetchall()`,
- plain `psycopg` instead of an ORM.

This is intentional for the current learning stage. It keeps the SQL visible and makes joins, filters and aggregations easier to understand.

## Write Operations

### Create measurement

`create_measurement(conn, measurement_data)` inserts a new measurement and uses PostgreSQL `RETURNING` to return the stored record with its generated `measurement_id`.

### Update quality status

`update_measurement_quality_status(conn, measurement_id, quality_status)` updates one measurement and returns the updated record.

Both write operations commit the transaction after successful execution.

## KPI Queries

Current KPI queries calculate:

- number of valid measurements,
- average load,
- minimum load,
- maximum load,
- latest measurement timestamp.

Global KPI endpoint:

```text
all valid measurements
```

Station-specific KPI endpoint:

```text
valid measurements for one station_id
```

## Test Database

Automated tests use a dedicated PostgreSQL test database:

```text
energy_operations_test
```

The test database is reset from `sql/test_seed_data.sql` in `tests/conftest.py`.

The reset uses deterministic seed data so exact KPI assertions remain stable.

## Current Limitations

The database layer is intentionally simple.

Current limitations:

- no migrations yet,
- no SQLAlchemy/Alembic yet,
- no repository/service layer yet,
- no central database exception handling yet,
- no transaction rollback fixture per test yet,
- no Dockerized PostgreSQL setup yet,
- no indexes beyond primary/foreign key basics yet,
- no alert, user or device tables yet.

These limitations are acceptable for the current stage. The next database-related improvements should focus on robustness, clearer structure and Docker readiness before adding larger new features.

## Next Database Improvements

Recommended next steps:

1. Review database error handling around connection and query failures.
2. Decide when route logic should move toward router/service separation.
3. Prepare Docker or Docker Compose for a reproducible PostgreSQL setup.
4. Consider migrations later after the current SQL-first learning phase is stable.
5. Plan future schema extensions such as alerts, devices, grid sections or users only after the MVP core is stable.
