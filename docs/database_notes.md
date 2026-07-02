# Database Notes

## Purpose

This document explains the database design and PostgreSQL integration of the **Energy Operations Platform**.

The README gives a high-level project overview. This file is intentionally more technical and focuses on:

- the relational database model,
- PostgreSQL table relationships,
- SQL concepts practiced in the project,
- Python database access with `psycopg`,
- database result mapping,
- measurement creation through parameterized SQL inserts,
- FastAPI path and query parameter behavior,
- FastAPI API documentation metadata,
- Pydantic request and response models,
- automated API tests with pytest and FastAPI TestClient,
- and how the database layer is used by the terminal workflow and the FastAPI API layer.

---

## Why Move from CSV to a Database?

Earlier project versions used a CSV file as the main data source.

Example:

```csv
Station,Load1,Load2,Load3
Station A,80,95,120
```

This was useful for learning Python basics, file handling, validation, error handling and object-oriented programming.

However, CSV files have important limitations for a backend-oriented energy platform:

- the number of load values is fixed by columns,
- measurement values do not have proper timestamps,
- metadata such as source or quality status is difficult to model,
- historical queries are inefficient,
- relationships between technical assets and measurements are not explicit,
- and the structure does not scale well toward APIs, dashboards or cloud services.

The current PostgreSQL model separates relatively stable station data from time-based measurement data.

---

## Relational Data Model

The first relational model contains two main tables:

- `stations`
- `measurements`

Relationship:

```text
One station can have many measurements.
Each measurement belongs to exactly one station.
```

This is implemented with a foreign key:

```text
measurements.station_id → stations.station_id
```

---

## Table: `stations`

The `stations` table stores relatively stable asset information.

Current fields:

| Field | Purpose |
|---|---|
| `station_id` | Primary key of the station |
| `station_name` | Human-readable station name |
| `station_type` | Technical asset type, e.g. `solar_park`, `wind_park`, `battery_storage` |
| `station_location` | Station location |
| `created_at` | Timestamp when the record was created |

Example:

| station_id | station_name | station_type | station_location |
|---:|---|---|---|
| 1 | Station A | solar_park | Stuttgart |
| 2 | Station B | wind_park | Ulm |
| 3 | Station C | hydro_power | Heidelberg |

---

## Table: `measurements`

The `measurements` table stores time-based measurement values.

Current fields:

| Field | Purpose |
|---|---|
| `measurement_id` | Primary key of the measurement |
| `station_id` | Foreign key to the related station |
| `measurement_time` | Timestamp of the measurement |
| `load_value` | Measured load value |
| `unit` | Measurement unit, currently `kW` |
| `source` | Data source |
| `quality_status` | Basic quality flag |
| `created_at` | Timestamp when the record was created |

Example:

| measurement_id | station_id | measurement_time | load_value | unit |
|---:|---:|---|---:|---|
| 1 | 1 | 2026-06-22 08:15 | 80.50 | kW |
| 2 | 1 | 2026-06-22 08:30 | 95.25 | kW |
| 3 | 2 | 2026-06-22 08:15 | 120.75 | kW |

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

The foreign key is:

```text
measurements.station_id
```

It refers to:

```text
stations.station_id
```

This means PostgreSQL enforces that a measurement can only exist for an existing station.

---

## Foreign Key Test

The foreign key constraint was tested by trying to insert a measurement with a non-existing `station_id`.

PostgreSQL rejected the insert because no station with this ID exists.

This confirms that the relationship between `stations` and `measurements` is enforced at database level, not only in Python code.

---

## SQL Files

The SQL files are stored in the `sql/` directory.

| File | Purpose |
|---|---|
| `sql/schema.sql` | Defines the `stations` and `measurements` tables |
| `sql/seed_data.sql` | Inserts example station and measurement data |
| `sql/example_queries.sql` | Contains example queries for filtering, joining and aggregating data |

---

## SQL Concepts Practiced

The project currently includes example queries for:

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

These queries make it possible to calculate basic energy-related KPIs directly in the database.

Examples:

- number of measurements per station,
- average load per station,
- minimum and maximum load per station,
- average load per station type,
- high-load filtering,
- grouped filtering with `HAVING`.

Important distinction:

```text
WHERE  = filters individual rows before grouping
HAVING = filters grouped results after aggregation
```

---

## Python Database Integration

The Python project connects to PostgreSQL using:

- `psycopg`
- `python-dotenv`

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

A safe `.env.example` file is committed to document the required variables.

---

## Current Database Module

The main database logic is located in:

```text
src/database.py
```

Current responsibilities:

- load database configuration from environment variables,
- open PostgreSQL connections,
- execute read queries,
- insert new measurement records,
- map database rows into dictionaries,
- provide reusable database functions for the terminal workflow and FastAPI endpoints.

---

## Current Database Functions

### `get_connection()`

Opens a PostgreSQL connection using environment variables.

Used by:

- `src/main.py`
- `src/api.py`

### `fetch_stations(conn)`

Reads all station data from the `stations` table.

Returned fields:

```text
station_id, station_name, station_type, station_location
```

Returned structure:

```python
[
    {
        "station_id": 1,
        "station_name": "Station A",
        "station_type": "solar_park",
        "station_location": "Stuttgart"
    }
]
```

### `fetch_station_by_id(conn, station_id)`

Reads one station by ID.

Expected behavior:

```text
Existing station     → returns one station dictionary
Non-existing station → returns None
```

This function is used by the FastAPI detail endpoint and by nested station/measurement endpoints to distinguish between:

```text
Station does not exist
```

and:

```text
Station exists, but has no measurements
```

### `fetch_joined_measurements(conn)`

Reads joined station and measurement data.

Returned fields:

```text
station_name, measurement_time, load_value, unit
```

This is used for the general measurement overview endpoint and the terminal report.

### `fetch_measurements_by_station_id(conn, station_id)`

Reads all measurements for a specific station.

The SQL query uses a parameterized query:

```sql
WHERE s.station_id = %s
```

with:

```python
(station_id,)
```

This avoids inserting user input directly into the SQL string and is the correct pattern for safe SQL execution.

Expected behavior:

```text
Station has measurements       → returns a list of measurement dictionaries
Station has no measurements    → returns []
Station does not exist         → handled by the API layer before this function is called
```

### `fetch_measurement_by_id(conn, measurement_id)`

Reads one detailed measurement record by measurement ID.

Returned fields:

```text
measurement_id, station_id, measurement_time, load_value, unit, source, quality_status
```

Expected behavior:

```text
Existing measurement     → returns one detailed measurement dictionary
Non-existing measurement → returns None
```

This function is used by:

```text
GET /measurements/{measurement_id}
```

The endpoint uses this distinction to return either a detailed measurement response or a `404 Not Found` error.

### `create_measurement(conn, measurement_data)`

Creates a new measurement record in PostgreSQL.

The function uses a parameterized SQL insert:

```sql
INSERT INTO measurements (...)
VALUES (%s, %s, %s, %s, %s, %s)
RETURNING measurement_id, station_id, measurement_time, load_value, unit, source, quality_status;
```

The `RETURNING` clause is important because PostgreSQL creates the new `measurement_id`. The API can return the saved record immediately after insertion.

The function calls:

```python
conn.commit()
```

so that the new measurement is persisted in the database.

Used by:

```text
POST /measurements
```

Expected behavior:

```text
Valid measurement data → inserts row and returns detailed measurement dictionary
Invalid station_id     → handled by API layer before insert
Invalid request body   → rejected by Pydantic before database access
```

### `fetch_database_report_data()`

Coordinates the terminal database report loading process:

- opens a database connection,
- loads station data,
- loads joined measurement data,
- returns both mapped result sets,
- closes the database connection.

This function is mainly used by the terminal workflow in `src/main.py`.

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

Example of a mapped measurement overview dictionary:

```python
{
    "station_name": "Station A",
    "measurement_time": "...",
    "load_value": 80.50,
    "unit": "kW"
}
```

Example of a mapped detailed measurement dictionary:

```python
{
    "measurement_id": 42,
    "station_id": 1,
    "measurement_time": "...",
    "load_value": 123.45,
    "unit": "kW",
    "source": "pytest",
    "quality_status": "valid"
}
```

This improves readability because later code can access values by name instead of by tuple position.

Example:

```python
station["station_name"]
measurement["load_value"]
```

This structure also works well with FastAPI because dictionaries can be returned as JSON responses.

---

## Terminal Workflow

The PostgreSQL-based terminal workflow is started with:

```bash
python -m src.main
```

Current flow:

1. `src/main.py` starts the application.
2. `src/database.py` opens a PostgreSQL connection.
3. `fetch_database_report_data()` loads station and measurement data.
4. `src/output.py` prints the database report to the terminal.
5. The database connection is closed safely.
6. Runtime information is written to the local log file.

This workflow is preserved for learning, testing and comparison with the API layer.

---

## FastAPI Database Flow

The FastAPI application is started with:

```bash
uvicorn src.api:app --reload
```

The API layer is defined in:

```text
src/api.py
```

The FastAPI app also contains project-specific OpenAPI metadata such as API title, description, version, tags, endpoint summaries, endpoint descriptions, parameter descriptions, response descriptions and Pydantic response schemas.

Current FastAPI endpoints using database data:

| Method | Endpoint | Database function used | Notes |
|---|---|---|---|
| `GET` | `/stations` | `fetch_stations(conn)` | Can optionally filter the returned list by `station_type`. |
| `GET` | `/stations/{station_id}` | `fetch_station_by_id(conn, station_id)` | Returns one station or `404 Not Found`. |
| `GET` | `/measurements` | `fetch_joined_measurements(conn)` | Can optionally limit the returned list with `limit`. |
| `GET` | `/measurements/{measurement_id}` | `fetch_measurement_by_id(conn, measurement_id)` | Returns one detailed measurement or `404 Not Found`. |
| `POST` | `/measurements` | `fetch_station_by_id(conn, station_id)` and `create_measurement(conn, measurement_data)` | Checks that the station exists before inserting a new measurement. |
| `GET` | `/stations/{station_id}/measurements` | `fetch_station_by_id(conn, station_id)` and `fetch_measurements_by_station_id(conn, station_id)` | Checks the parent station before loading measurements; can optionally limit the returned list with `limit`. |

Current API flow per database-backed request:

1. FastAPI receives the HTTP request.
2. The endpoint opens a database connection.
3. The required database function is called.
4. The result is returned as JSON.
5. The database connection is closed safely.

Example:

```text
GET /stations/1/measurements
→ check whether station 1 exists
→ load measurements for station 1
→ return measurement list as JSON
```

Example write flow:

```text
POST /measurements
→ validate JSON request body with MeasurementCreate
→ check whether the referenced station exists
→ insert measurement into PostgreSQL
→ commit transaction
→ return created measurement with measurement_id
```

Example detail flow:

```text
GET /measurements/42
→ load measurement 42 from PostgreSQL
→ return detailed measurement as JSON
```

---

## API Query Parameters

The API currently uses query parameters for optional filtering and limiting.

Query parameters do not identify one specific resource. Instead, they modify how a list endpoint is returned.

Examples:

```text
GET /stations?station_type=solar_park
GET /measurements?limit=5
GET /stations/1/measurements?limit=5
```

Current query parameters:

| Endpoint | Query parameter | Purpose | Behavior |
|---|---|---|---|
| `/stations` | `station_type` | Filters stations by technical asset type. | Unknown types return an empty list `[]`. |
| `/measurements` | `limit` | Limits the number of returned measurement records. | Invalid values are rejected by FastAPI validation. |
| `/stations/{station_id}/measurements` | `limit` | Limits the number of returned measurement records for one station. | Invalid values are rejected by FastAPI validation. |

The `limit` parameter is validated with FastAPI `Query` constraints. Current behavior:

| Request example | Result |
|---|---|
| `/measurements` | Returns all measurements. |
| `/measurements?limit=5` | Returns the first 5 measurements. |
| `/measurements?limit=0` | Returns `422 Unprocessable Content`. |
| `/measurements?limit=-1` | Returns `422 Unprocessable Content`. |
| `/measurements?limit=101` | Returns `422 Unprocessable Content` if the configured upper limit is 100. |
| `/measurements?limit=abc` | Returns `422 Unprocessable Content` because the value is not an integer. |

The same `limit` validation pattern is also used by the nested station measurement endpoint:

| Request example | Result |
|---|---|
| `/stations/1/measurements` | Returns all measurements for station `1`. |
| `/stations/1/measurements?limit=5` | Returns the first 5 measurements for station `1`. |
| `/stations/1/measurements?limit=0` | Returns `422 Unprocessable Content`. |
| `/stations/1/measurements?limit=abc` | Returns `422 Unprocessable Content` because the value is not an integer. |

The `station_type` parameter currently filters in Python after loading station data from the database. This is intentionally simple for the current learning stage. Later, filtering can be moved into SQL for larger datasets.

---

## FastAPI Documentation and Parameter Validation

The API documentation has been improved in `v0.5.1`. This is mainly a polish step for Swagger/OpenAPI and does not change the underlying database model.

Current documentation improvements:

| Area | Current implementation | Benefit |
|---|---|---|
| API metadata | Custom title, description and version | Swagger UI clearly identifies the portfolio API. |
| Tags | `General`, `Stations`, `Measurements` | Endpoints are grouped by responsibility. |
| Summaries | Short route summaries | The endpoint overview is easier to scan. |
| Descriptions | Longer route descriptions | API behavior is easier to understand without reading the code. |
| Response descriptions | Documented response meaning | Swagger UI explains what each route returns. |
| Query parameter descriptions | `station_type`, `limit` | Optional filters are documented directly in the API docs. |
| Path parameter descriptions | `station_id` | Station-specific routes are easier to understand. |

Current validation behavior:

| Parameter | Location | Constraint | Example invalid request | Result |
|---|---|---|---|---|
| `station_id` | Path | Integer, minimum `1` | `/stations/0` | `422 Unprocessable Content` |
| `station_id` | Path | Integer, minimum `1` | `/stations/abc` | `422 Unprocessable Content` |
| `limit` | Query | Integer, minimum `1`, maximum `100` | `/measurements?limit=0` | `422 Unprocessable Content` |
| `limit` | Query | Integer, minimum `1`, maximum `100` | `/measurements?limit=101` | `422 Unprocessable Content` |
| `limit` | Query | Integer, minimum `1`, maximum `100` | `/stations/1/measurements?limit=0` | `422 Unprocessable Content` |
| `measurement_id` | Path | Integer, minimum `1` | `/measurements/0` | `422 Unprocessable Content` |
| `measurement_id` | Path | Integer, minimum `1` | `/measurements/abc` | `422 Unprocessable Content` |
| `station_id` | Request body | Integer, minimum `1` | `POST /measurements` with `station_id = 0` | `422 Unprocessable Content` |
| `load_value` | Request body | Number, minimum `0` | `POST /measurements` with negative load value | `422 Unprocessable Content` |
| `unit` | Request body | Allowed values `kW`, `MW` | `POST /measurements` with `unit = "kWh"` | `422 Unprocessable Content` |
| `source` | Request body | Non-empty string | `POST /measurements` with empty source | `422 Unprocessable Content` |
| `quality_status` | Request body | Allowed values `valid`, `invalid`, `estimated` | `POST /measurements` with invalid status | `422 Unprocessable Content` |

---

## Pydantic Request and Response Models

The FastAPI layer uses Pydantic models for both API responses and JSON request bodies.

The models are defined in:

```text
src/schemas.py
```

Current models:

### `StationResponse`

Used for station endpoints.

Fields:

```text
station_id: int
station_name: str
station_type: str
station_location: str
```

Used by:

```text
GET /stations
GET /stations/{station_id}
```

### `MeasurementResponse`

Used for measurement overview endpoints.

Fields:

```text
station_name: str
measurement_time: datetime
load_value: float
unit: str
```

Used by:

```text
GET /measurements
GET /stations/{station_id}/measurements
```

This model is intentionally smaller than the full measurement record because it represents joined overview data that includes the station name.

### `MeasurementCreate`

Used as the request body model for creating new measurement records.

Fields:

```text
station_id: int
measurement_time: datetime
load_value: float
unit: Literal["kW", "MW"]
source: str
quality_status: Literal["valid", "invalid", "estimated"]
```

Used by:

```text
POST /measurements
```

Current validation rules:

| Field | Rule |
|---|---|
| `station_id` | Must be at least `1`. |
| `measurement_time` | Must be a valid date-time value. |
| `load_value` | Must be greater than or equal to `0`. |
| `unit` | Must be one of `kW` or `MW`. |
| `source` | Must be a non-empty string. |
| `quality_status` | Must be one of `valid`, `invalid` or `estimated`. |

Invalid request bodies are rejected by FastAPI/Pydantic before the database insert is executed.

### `MeasurementDetailResponse`

Used for detailed measurement responses.

Fields:

```text
measurement_id: int
station_id: int
measurement_time: datetime
load_value: float
unit: str
source: str
quality_status: str
```

Used by:

```text
POST /measurements
GET /measurements/{measurement_id}
```

This model represents a complete measurement record as returned by the database.

### Why These Models Matter

Before the API used Pydantic models, dictionaries were returned directly. This worked, but the public API contract was implicit.

With request and response models:

- Swagger UI shows explicit request and response schemas,
- FastAPI validates that returned data matches the declared response schema,
- FastAPI validates incoming JSON before database writes happen,
- invalid payloads return consistent `422 Unprocessable Content` responses,
- station and measurement response structures are easier to understand,
- and automated API tests can check stable API contracts.

`measurement_time` is modeled as a Python `datetime`. In JSON responses, FastAPI/Pydantic serializes it in ISO 8601 format:

```json
"2026-06-22T08:15:00"
```

This is standard API behavior and should not be changed to a manually formatted string unless there is a specific client requirement.

## Automated API Tests

In `v0.5.3`, automated API tests were added with pytest and FastAPI `TestClient`.

The tests are located in:

```text
tests/test_api.py
```

They are executed from the project root with:

```bash
py -m pytest -v
```

Current test coverage:

| Test area | Examples | Expected behavior |
|---|---|---|
| General endpoints | `/`, `/health` | Return `200 OK` and expected JSON responses. |
| Station list | `/stations` | Returns a list with station dictionaries matching the API schema. |
| Station type filter | `/stations?station_type=unknown` | Returns `200 OK` with an empty list `[]`. |
| Station detail | `/stations/1` | Returns one station object. |
| Station not found | `/stations/9999` | Returns `404 Not Found`. |
| Invalid station path values | `/stations/0`, `/stations/abc` | Return `422 Unprocessable Content`. |
| Measurement list | `/measurements` | Returns a list with measurement dictionaries matching the API schema. |
| Measurement limit | `/measurements?limit=5` | Returns at most five records. |
| Invalid measurement limit | `/measurements?limit=0`, `/measurements?limit=101`, `/measurements?limit=abc` | Return `422 Unprocessable Content`. |
| Measurement creation | `POST /measurements` | Creates a new measurement and returns `201 Created`. |
| Measurement creation validation | negative load, invalid unit, invalid quality status, empty or missing source | Return `422 Unprocessable Content`. |
| Measurement creation not found | `POST /measurements` with unknown station ID | Returns `404 Not Found`. |
| Measurement detail | `/measurements/{measurement_id}` | Returns one detailed measurement record. |
| Measurement detail errors | `/measurements/0`, `/measurements/abc`, unknown measurement ID | Return expected `422` or `404` responses. |
| Create-then-read flow | `POST /measurements` followed by `GET /measurements/{measurement_id}` | Confirms that a created measurement can be retrieved by its generated ID. |
| Nested station measurements | `/stations/1/measurements` | Returns measurements for one station. |
| Nested endpoint errors | `/stations/9999/measurements`, `/stations/abc/measurements`, `/stations/1/measurements?limit=0` | Return expected `404` or `422` responses. |

The current tests are integration-style API tests. They import the real FastAPI app from `src.api` and call endpoints through `TestClient`.

Important current limitation:

```text
The tests use the local PostgreSQL database and existing seed data.
```

This is acceptable for the current learning stage because it verifies the real FastAPI-to-database flow. Later improvements can introduce:

- a separate test database,
- test fixtures,
- dependency overrides,
- mocked database access,
- or CI execution through GitHub Actions.

## API Error Behavior

The API distinguishes between different cases.

### Existing station with measurements

```text
GET /stations/1/measurements
```

Result:

```text
200 OK
```

with a list of measurement dictionaries.

### Existing station without measurements

Result:

```text
200 OK
```

with an empty list:

```json
[]
```

This is correct because the station exists. The query result is simply empty.

### Non-existing station

```text
GET /stations/999/measurements
```

Result:

```text
404 Not Found
```

because the parent station does not exist.

### Invalid path parameter type

```text
GET /stations/abc
```

Result:

```text
422 Unprocessable Content
```

FastAPI returns this automatically because `station_id` is typed as `int`.

### Invalid path parameter range

```text
GET /stations/0
```

Result:

```text
422 Unprocessable Content
```

FastAPI returns this because `station_id` is constrained to a minimum value of `1`.

### Query parameter without matching results

```text
GET /stations?station_type=unknown
```

Result:

```text
200 OK
```

with an empty list:

```json
[]
```

This is correct because the list endpoint exists. The filter simply has no matching records.

### Invalid query parameter value

```text
GET /measurements?limit=-1
```

Result:

```text
422 Unprocessable Content
```

FastAPI returns this because the `limit` query parameter is constrained to valid positive values.

### Creating a measurement

```text
POST /measurements
```

with a valid request body creates a new measurement record in PostgreSQL.

Result:

```text
201 Created
```

The response contains the new `measurement_id` generated by the database.

### Creating a measurement for a non-existing station

```text
POST /measurements
```

with an unknown `station_id` returns:

```text
404 Not Found
```

The API checks the parent station before inserting the measurement. This produces a clearer API error than relying only on the database foreign key error.

### Invalid measurement creation payload

Invalid request body values return:

```text
422 Unprocessable Content
```

Examples include:

- negative `load_value`,
- invalid `unit`,
- invalid `quality_status`,
- missing or empty `source`,
- invalid `station_id`.

### Reading a measurement by ID

```text
GET /measurements/42
```

returns one detailed measurement record if the measurement exists.

### Non-existing measurement ID

```text
GET /measurements/999999999
```

returns:

```text
404 Not Found
```

because no measurement with this ID exists.

### Invalid measurement ID

```text
GET /measurements/0
GET /measurements/abc
```

returns:

```text
422 Unprocessable Content
```

because `measurement_id` is constrained to an integer with a minimum value of `1`.

---

## Output Separation

Database access, terminal output and API responses are separated.

Current structure:

```text
src/database.py → database connection and queries
src/output.py   → terminal output formatting
src/main.py     → terminal application flow
src/api.py      → FastAPI routes and JSON responses
src/schemas.py  → Pydantic response models for API response schemas
```

This separation is important because the same database layer can be used by different application interfaces.

---

## Logging

Logging is configured centrally in:

```text
src/logging_config.py
```

The logging setup is used by both:

- the terminal workflow,
- the FastAPI application.

The local log directory is created automatically if needed.

The generated log file is local runtime data and should not be committed.

---

## Legacy CSV/OOP Workflow

The earlier CSV/OOP workflow is preserved in:

```text
demos/legacy_csv_demo.py
```

It uses:

- `data/stations.csv`
- `src/read_documents.py`
- `src/station.py`
- `src/server.py`

This workflow demonstrates the earlier project stage:

```text
CSV data → Station objects → Python report
```

The current main workflow is:

```text
PostgreSQL data → Python database layer → terminal report and FastAPI JSON API
```

---

## Current Limitations

The current implementation is intentionally simple.

Current limitations:

- Python currently supports reading from PostgreSQL and inserting new measurement records.
- No update/delete operations from Python yet.
- Database result mapping still uses dictionaries internally before FastAPI validates the response models.
- API routes are still kept in `src/api.py`; routers can be introduced later when the API grows.
- Current query parameter filtering is intentionally simple and partly happens in Python instead of SQL.
- Error handling around database connection failures is still basic.
- Automated tests currently use the local PostgreSQL database instead of an isolated test database.
- No Docker setup yet.
- No cloud deployment yet.

These limitations are intentional for the current learning stage.

---

## Completed in v0.4

- Created first relational PostgreSQL schema.
- Created `stations` and `measurements` tables.
- Added primary keys and foreign key relationship.
- Inserted example station and measurement data.
- Added SQL example queries.
- Practiced filtering, joining and aggregating data.
- Connected Python to PostgreSQL using `psycopg`.
- Loaded database configuration from environment variables.
- Read station data from PostgreSQL.
- Read joined station and measurement data from PostgreSQL.
- Separated database access from terminal output formatting.
- Preserved the old CSV/OOP workflow as a legacy demo.
- Reorganized project files into `src/`, `sql/`, `docs/`, `data/` and `demos/`.

---

## Completed in v0.4.1

- Mapped PostgreSQL result rows into dictionaries with explicit field names.
- Replaced tuple-position access with dictionary-key access for database results.
- Prepared station and measurement data for JSON responses in the later FastAPI layer.
- Improved readability of downstream code by using keys such as `station_name`, `station_type`, `measurement_time` and `load_value`.

---

## Completed in v0.5

- Added a first FastAPI application.
- Added health and welcome endpoints.
- Added `/stations` endpoint.
- Added `/stations/{station_id}` endpoint with path parameter and 404 behavior.
- Added `/measurements` endpoint.
- Added `/stations/{station_id}/measurements` endpoint.
- Returned PostgreSQL-backed station and measurement data as JSON.
- Added automatic API documentation through OpenAPI/Swagger UI.
- Centralized logging configuration for terminal and API workflows.
- Kept database access separated from API route definitions.
- Added query parameters for list endpoints, including `station_type` on `/stations` and `limit` on `/measurements`.

---

## Completed in v0.5.1

- Added project-specific FastAPI metadata: API title, description and version.
- Added OpenAPI tags for grouping endpoints in Swagger UI.
- Added endpoint summaries, descriptions and response descriptions.
- Added descriptions for path and query parameters.
- Added `Path` constraints for `station_id` so invalid values such as `0` are rejected.
- Kept the release intentionally small as API documentation and validation polish before introducing Pydantic response models.

---

## Completed in v0.5.2

- Added `src/schemas.py` for Pydantic response models.
- Added `StationResponse` for station API responses.
- Added `MeasurementResponse` for measurement API responses.
- Connected FastAPI endpoints to response models through `response_model`.
- Validated the difference between list responses and single-object responses.
- Confirmed that `measurement_time` is returned in standard ISO 8601 date-time format.
- Improved Swagger/OpenAPI output with explicit response schemas.

---

## Completed in v0.5.3

- Added `tests/test_api.py` for automated FastAPI endpoint tests.
- Added pytest-based tests using FastAPI `TestClient`.
- Tested general endpoints such as `/` and `/health`.
- Tested station list and station detail endpoints.
- Tested query parameter behavior for station type filtering.
- Tested measurement list endpoints and `limit` behavior.
- Tested nested station measurement endpoints.
- Tested expected `404 Not Found` behavior for non-existing stations.
- Tested expected `422 Unprocessable Content` behavior for invalid path and query parameters.
- Confirmed that the current FastAPI/PostgreSQL integration can be checked automatically with a single pytest command.

## Completed in v0.6.0

- Added the first write endpoint: `POST /measurements`.
- Added `MeasurementCreate` as request body model for measurement creation.
- Added `MeasurementDetailResponse` for full measurement responses.
- Added `create_measurement(conn, measurement_data)` in `src/database.py`.
- Used a parameterized `INSERT INTO measurements (...) VALUES (...)` query.
- Used PostgreSQL `RETURNING` to get the created measurement including its generated `measurement_id`.
- Added `conn.commit()` after successful insert.
- Added `201 Created` as the successful response status for measurement creation.
- Checked whether the referenced station exists before inserting the measurement.
- Returned `404 Not Found` when trying to create a measurement for a non-existing station.

## Completed in v0.6.1

- Added request validation for measurement creation.
- Added Pydantic `Field` constraints for values such as `station_id` and `load_value`.
- Added constrained allowed values for `unit` and `quality_status`.
- Rejected invalid measurement creation payloads with `422 Unprocessable Content`.
- Added automated tests for invalid payload cases, including negative load values, invalid units, invalid quality status and empty or missing source fields.

## Completed in v0.6.2

- Added `GET /measurements/{measurement_id}`.
- Added `fetch_measurement_by_id(conn, measurement_id)` in `src/database.py`.
- Added detailed measurement mapping for full measurement records.
- Returned `404 Not Found` for non-existing measurement IDs.
- Added `Path(..., ge=1)` validation for `measurement_id`.
- Added automated tests for measurement detail success, not-found cases and invalid measurement IDs.
- Added a create-then-read API flow test that creates a measurement and retrieves it again by the generated `measurement_id`.

---

## Next Steps

Recommended next steps:

1. Add a targeted update endpoint for measurement quality status, for example `PATCH /measurements/{measurement_id}/quality-status`.
2. Improve database error handling.
3. Add more realistic database queries and KPI endpoints.
4. Introduce routers later when the API contains more endpoints.
5. Add Docker setup for the application and PostgreSQL.
6. Prepare a simple cloud deployment scenario.
