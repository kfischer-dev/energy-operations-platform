# Database Notes

## Purpose

This document describes the database design and PostgreSQL integration of the Energy Operations Platform.

The goal is to move from a CSV-based data structure toward a relational database model that can later support backend services, REST APIs, cloud deployment and energy-related data analysis.

---

## Why Move from CSV to a Database?

The earlier project versions used a CSV file as the main data source.

Example:

```csv
Station,Load1,Load2,Load3
Station A,80,95,120
```

This was useful for learning Python basics, file handling, error handling and object-oriented programming.

However, a CSV-based structure has important limitations:

* the number of load values is fixed by columns,
* measurement values do not have proper timestamps,
* metadata such as source or quality status is difficult to store,
* historical queries are inefficient,
* relationships between technical assets and measurements are not explicit,
* and the structure does not scale well toward APIs or backend services.

For a backend-oriented energy data platform, stations and measurements should be modeled separately.

---

## Relational Data Model

The first relational model separates technical assets from measurement values.

The two main tables are:

* `stations`
* `measurements`

This reflects a typical real-world structure:

```text
One station can have many measurements.
Each measurement belongs to exactly one station.
```

---

## Table: `stations`

The `stations` table stores relatively stable asset information.

Current fields:

* `station_id`
* `station_name`
* `station_type`
* `station_location`
* `created_at`

Example:

| station_id | station_name | station_type | station_location |
| ---------: | ------------ | ------------ | ---------------- |
|          1 | Station A    | solar_park   | Stuttgart        |
|          2 | Station B    | wind_park    | Ulm              |
|          3 | Station C    | hydro_power  | Heidelberg       |

---

## Table: `measurements`

The `measurements` table stores changing measurement values.

Current fields:

* `measurement_id`
* `station_id`
* `measurement_time`
* `load_value`
* `unit`
* `source`
* `quality_status`
* `created_at`

Example:

| measurement_id | station_id | measurement_time | load_value | unit |
| -------------: | ---------: | ---------------- | ---------: | ---- |
|              1 |          1 | 2026-06-22 08:15 |      80.50 | kW   |
|              2 |          1 | 2026-06-22 08:30 |      95.25 | kW   |
|              3 |          2 | 2026-06-22 08:15 |     120.75 | kW   |

---

## Primary Key and Foreign Key

Each station has a unique primary key:

```text
stations.station_id
```

Each measurement has its own unique primary key:

```text
measurements.measurement_id
```

The field `measurements.station_id` is a foreign key that refers to `stations.station_id`.

Relationship:

```text
stations.station_id → measurements.station_id
```

This enforces that each measurement belongs to an existing station.

---

## Foreign Key Test

The foreign key constraint was tested by trying to insert a measurement with a non-existing `station_id`.

PostgreSQL rejected the insert because no station with this ID exists.

This confirms that the relationship between `stations` and `measurements` is enforced by the database.

---

## SQL Files

The SQL files are stored in the `sql/` directory.

| File                      | Purpose                                                               |
| ------------------------- | --------------------------------------------------------------------- |
| `sql/schema.sql`          | Defines the database tables.                                          |
| `sql/seed_data.sql`       | Inserts example station and measurement data.                         |
| `sql/example_queries.sql` | Contains example queries for filtering, joining and aggregating data. |

---

## SQL Concepts Practiced

The project currently includes example queries for:

* `SELECT`
* `WHERE`
* `JOIN`
* `ORDER BY`
* `COUNT`
* `AVG`
* `MIN`
* `MAX`
* `GROUP BY`
* `HAVING`

These queries make it possible to calculate basic energy KPIs directly in the database.

Examples:

* number of measurements per station,
* average load per station,
* minimum and maximum load per station,
* average load per station type,
* high-load filtering,
* grouped filtering with `HAVING`.

Important distinction:

```text
WHERE  = filters individual rows before grouping
HAVING = filters grouped results after aggregation
```

---

## Python Database Integration

The Python project connects to PostgreSQL using:

* `psycopg`
* `python-dotenv`

Database credentials are not stored directly in the Python code.

Instead, local connection data is read from a `.env` file.

Example `.env` structure:

```env
DB_NAME=energy_operations
DB_USER=postgres
DB_PASSWORD=your_local_password
DB_HOST=localhost
DB_PORT=5432
```

The real `.env` file must not be committed to GitHub.

A safe `.env.example` file should be committed to document the required variables.

---

## Current Python Database Flow

The current PostgreSQL-based application flow is started with:

```bash
python -m src.main
```

Current flow:

1. `src/main.py` starts the application.
2. `src/database.py` loads database credentials from environment variables.
3. `src/database.py` opens a PostgreSQL connection.
4. `fetch_stations()` reads station records from PostgreSQL.
5. `fetch_joined_measurements()` reads joined station and measurement records.
6. `fetch_database_report_data()` returns mapped station and measurement dictionaries.
7. `src/output.py` prints the database report to the terminal.
8. The database connection is closed safely.

---

## Current Database Functions

### `get_connection()`

Opens a PostgreSQL connection using environment variables.

### `fetch_stations(conn)`

Reads station data from the `stations` table.

Mapped result fields:

```text
station_id, station_name, station_type, station_location
```

### `fetch_joined_measurements(conn)`

Reads measurement data joined with station names.

Mapped result fields:

```text
station_name, measurement_time, load_value, unit
```

### `fetch_database_report_data()`

Coordinates the database report loading process:

* opens a connection,
* loads station data,
* loads joined measurement data,
* maps raw database rows into dictionaries with explicit field names,
* closes the connection,
* returns both mapped result sets.

---

## Database Result Mapping

PostgreSQL query results are returned by `psycopg` as rows that behave like tuples.

Earlier versions passed these raw result rows directly through the application. This worked, but the data was position-based and therefore less readable.

Example of a raw station row:

```text
(1, "Station A", "solar_park", "Stuttgart")
```

The project now maps database rows into dictionaries with explicit field names.

Example of a mapped station dictionary:

```python
{
    "station_id": 1,
    "station_name": "Station A",
    "station_type": "solar_park",
    "station_location": "Stuttgart"
}
```

Example of a mapped measurement dictionary:

```python
{
    "station_name": "Station A",
    "measurement_time": "...",
    "load_value": 80.50,
    "unit": "kW"
}
```

This improves readability because later code can access values by name instead of by tuple position.

Example:

```python
station["station_name"]
measurement["load_value"]
```

This structure also prepares the project for future FastAPI endpoints, where dictionary-like data can later be returned as JSON responses.

---

## Output Separation

Database access and output formatting are separated.

Current structure:

```text
src/database.py → database connection and queries
src/output.py   → terminal output formatting
src/main.py     → application flow
```

This separation is important because later versions may return the same data through FastAPI instead of printing it to the terminal.

---

## Legacy CSV/OOP Workflow

The earlier CSV/OOP workflow is preserved in:

```text
demos/legacy_csv_demo.py
```

It uses:

* `data/stations.csv`
* `src/read_documents.py`
* `src/station.py`
* `src/server.py`

This workflow demonstrates the earlier project stage:

```text
CSV data → Station objects → Python report
```

The current v0.4 focus is:

```text
PostgreSQL data → SQL queries → database report
```

---

## Project Structure After Reorganization

```text
energy-operations-platform/
│
├── data/
│   └── stations.csv
│
├── demos/
│   ├── database_test.py
│   └── legacy_csv_demo.py
│
├── docs/
│   └── database_notes.md
│
├── sql/
│   ├── schema.sql
│   ├── seed_data.sql
│   └── example_queries.sql
│
├── src/
│   ├── database.py
│   ├── main.py
│   ├── output.py
│   ├── read_documents.py
│   ├── server.py
│   └── station.py
│
├── README.md
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## Completed in v0.4

* Created first relational PostgreSQL schema.
* Created `stations` and `measurements` tables.
* Added primary keys and foreign key relationship.
* Inserted example station and measurement data.
* Added SQL example queries.
* Practiced filtering, joining and aggregating data.
* Connected Python to PostgreSQL using `psycopg`.
* Loaded database configuration from environment variables.
* Read station data from PostgreSQL.
* Read joined station and measurement data from PostgreSQL.
* Mapped PostgreSQL result rows into dictionaries with explicit field names.
* Separated database access from terminal output formatting.
* Preserved the old CSV/OOP workflow as a legacy demo.
* Reorganized project files into `src/`, `sql/`, `docs/`, `data/` and `demos/`.

---

## Current Limitations

The current implementation is intentionally simple.

Current limitations:

* Python only reads from PostgreSQL.
* No insert/update/delete operations from Python yet.
* Database result mapping is still simple and uses dictionaries instead of dedicated data objects or API schemas.
* No FastAPI endpoints yet.
* No automated tests yet.
* No Docker setup yet.
* No cloud deployment yet.

These limitations are intentional for the current learning stage.

---

## Next Steps

Recommended next steps:

1. Keep the v0.4 PostgreSQL integration stable.
2. Improve mapped database dictionaries step by step or introduce dedicated data objects/API schemas later.
3. Add basic error handling around database connection failures.
4. Add a first FastAPI endpoint for station data.
5. Add a first FastAPI endpoint for measurement data.
6. Return database data as JSON.
7. Add basic tests for database-related functions.
8. Add Docker setup for the application and PostgreSQL.
9. Prepare a simple cloud deployment scenario.
