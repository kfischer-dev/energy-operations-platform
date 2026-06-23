# Database Notes

## Purpose

This document describes the first database design ideas for the Energy Operations Platform.

The goal is to move from a CSV-based data structure toward a relational database model that can later support PostgreSQL, REST APIs and backend services.

---

## Current Data Structure

The current project reads station data from a CSV file.

Each row contains:

- a station name
- multiple load values

During import, each CSV row is converted into a `Station` object. Valid load values are stored and processed. Invalid or missing values are handled through logging.

---

## Why CSV Is Not Enough Long-Term

The current CSV structure is useful for learning and early prototyping, but it is limited for a real backend system.

Current structure:

```csv
Station,Load1,Load2,Load3
Station A,80,95,120
```

This structure has several limitations:

* the number of load values is fixed by the number of columns
* measurement values do not have timestamps
* measurements cannot easily store additional metadata
* different measurement types are difficult to represent
* querying historical data is inefficient
* relationships between technical assets and measurements are not explicit

For a backend-oriented energy data platform, stations and measurements should be modeled separately.

## Relational Data Model

The first relational model separates technical assets from measurement values.

This leads to two main tables:

* stations
* measurements

# Station Data

A station represents a technical asset. It changes rarely compared to measurement values. Examples could be a transformer station, wind park, solar park or industrial energy asset.

# Measurement Data

A measurement represents a changing value recorded for a station. In the current version, measurements are load values. Later versions may also include voltage, temperature, power output, status values or other technical measurements.

## Table: stations

The stations table stores relatively stable asset information.

Current fields:

* station_id
* station_name
* station_type
* station_location
* created_at

Example:

| station_id | station_name | station_type | station_location |
|---:|---|---|---|
| 1 | Station A | solar_park | Stuttgart |
| 2 | Station B | wind_park | Ulm |

## Table: measurements

The measurements table stores changing measurement values.

Current fields:

* measurement_id
* station_id
* measurement_time
* load_value
* unit
* source
* quality_status
* created_at

Example:

| measurement_id | station_id | measurement_time | load_value | unit |
|---:|---:|---|---:|---|
| 1 | 1 | 2026-06-22 08:00 | 80.50 | kW |
| 2 | 1 | 2026-06-22 08:15 | 95.25 | kW |
| 3 | 1 | 2026-06-22 08:30 | 120.75 | kW |

## Primary Key and Foreign Key

Each station has a unique `station_id`.

Each measurement also has a unique `measurement_id`.

The field `station_id` in the `measurements` table refers to the `station_id` of the related station.

This creates a relationship:

* stations.station_id → measurements.station_id

This makes it possible to store many measurements for one station.

## Design Decisions

The first database model separates stations and measurements because they represent different concepts.

A station is a technical asset and changes rarely.

A measurement is a recorded value and changes frequently.

This separation makes the system more flexible and prepares the project for future extensions such as:

* alerts
* asset types
* measurement history
* different measurement types
* REST API endpoints
* PostgreSQL integration

## Relationship Between Stations and Measurements

A station can have many measurements.

Each measurement belongs to exactly one station.

This is modeled as a one-to-many relationship:

stations.station_id → measurements.station_id

## Why This Relationship Is Useful

This structure allows the system to store a flexible number of measurements for each station. It also makes it possible to query all measurements for one station, calculate historical values and later add alerts or different measurement types.

## PostgreSQL Test

The initial schema was tested successfully in a local PostgreSQL database named `energy_operations`.

Tested concepts:

- table creation
- primary keys
- foreign key relationship
- insert statements
- select queries
- filtering with `WHERE`
- joining `stations` and `measurements`

## Progress and Next Steps

### Completed

- Defined the first relational table structure.
- Created an initial `schema.sql` draft.
- Practiced basic SQL commands:
  - `CREATE TABLE`
  - `INSERT INTO`
  - `SELECT`
  - `WHERE`
  - `JOIN`
- Installed PostgreSQL locally.
- Created a local PostgreSQL database named `energy_operations`.
- Tested the first schema successfully in PostgreSQL.
- Inserted example station and measurement data.
- Verified the relationship between `stations` and `measurements` using a `JOIN`.
- Renamed station columns from generic names to clearer names:
  - `name` → `station_name`
  - `location` → `station_location`
- Added additional example stations and measurement values.
- Added SQL aggregation examples using `COUNT`, `AVG`, `MIN`, `MAX`, `GROUP BY` and `HAVING`.
- Set up the first Python database connection preparation:
  - created `.venv`
  - installed `psycopg`
  - installed `python-dotenv`
  - created `requirements.txt`
  - created `.env` and `.env.example` for local database configuration.
- Created a local `.venv` for project-specific Python dependencies.
- Installed `psycopg` for PostgreSQL access from Python.
- Installed `python-dotenv` for loading local environment variables from `.env`.
- Created a `.env` file for local database connection settings.
- Created a `.env.example` file as a safe template without real secrets.
- Added Python dependencies to `requirements.txt`.
- Successfully connected to the local PostgreSQL database from Python.
- Executed a first `SELECT` query from Python.
- Printed station records from PostgreSQL in the terminal.

### Current Focus

- Keep the SQL work separated into clean project files:
  - `schema.sql` for table definitions
  - `seed_data.sql` for example data
  - `example_queries.sql` for test queries
- Read database configuration from `.env` instead of hardcoding credentials in Python.
- Test the PostgreSQL connection from Python using `psycopg`.
- Execute the first read-only `SELECT` query from Python.
- Keep the database model small and understandable before adding more Python business logic.

## Foreign Key Test

The foreign key constraint was tested by trying to insert a measurement with a non-existing `station_id`.

PostgreSQL rejected the insert because no station with this ID exists.

This confirms that the relationship between `stations` and `measurements` is enforced by the database.

## SQL Queries and Aggregations

The project now includes example SQL queries for filtering, joining and aggregating station measurement data.

Covered query concepts:

- `SELECT`
- `WHERE`
- `JOIN`
- `ORDER BY`
- `COUNT`
- `AVG`
- `MIN`
- `MAX`
- `GROUP BY`
- `HAVING`

These queries make it possible to calculate basic energy KPIs directly in the database, such as:

- number of measurements per station
- average load per station
- minimum and maximum load per station
- average load per station type
- filtering high load values
- filtering grouped results with `HAVING`

`WHERE` is used to filter individual rows before grouping.

`HAVING` is used to filter grouped results after aggregation.

## Python Database Connection

The next step is to connect the Python project to the local PostgreSQL database.

The application should not store database credentials directly in the Python code. Instead, local connection data is stored in a `.env` file.

Example `.env` structure:

```env
DB_NAME=energy_operations
DB_USER=postgres
DB_PASSWORD=your_local_password
DB_HOST=localhost
DB_PORT=5432
```

The real `.env` file must not be committed to GitHub.

A public `.env.example` file can be committed to document which environment variables are required.

Required Python packages:

```txt
psycopg[binary]
python-dotenv
```

`psycopg` is used to connect Python with PostgreSQL.

`python-dotenv` is used to load the local `.env` file into Python.

The first Python test should only read data from the database.

The first query should be simple:

```sql
SELECT station_id, station_name, station_type, station_location
FROM stations
ORDER BY station_id;
```

The result returned by PostgreSQL is not one large string. Python receives structured rows, usually as tuples. This means the data does not need to be split manually like CSV or TXT data.

Example result structure:

```python
[
    (1, "Station A", "solar_park", "Stuttgart"),
    (2, "Station B", "wind_park", "Ulm")
]
```

Later, these rows can be converted into Python objects or returned as JSON through FastAPI.

### Next Steps

- Refactor `database_test.py` so that the database connection is separated into a small helper function.
- Replace raw tuple output with clearer formatted terminal output.
- Add a first query for measurements joined with station data.
- Keep the first Python database access read-only for now (`SELECT` only).
- Do not insert, update or delete data from Python yet.
- Document that Python receives structured database rows, not raw strings that need manual splitting.
- Later move database access logic into a dedicated module, e.g. `database.py`.
- Later connect the PostgreSQL access layer to FastAPI endpoints.