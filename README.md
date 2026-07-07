# Energy Operations Platform

## Overview

The **Energy Operations Platform** is a Python-based backend and data project for processing, validating and exposing technical energy and station data.

The project started with CSV-based station data and object-oriented Python logic. It has since evolved into a PostgreSQL-backed backend application with a first FastAPI layer that exposes station and measurement data through REST endpoints.

This project is part of a structured learning path toward backend, data and cloud development with a focus on industrial and energy-related software systems.

---

## Project Goal

The goal of this project is to build a realistic technical backend and data platform step by step.

The long-term vision is a system that can:

* process technical asset and measurement data,
* validate incoming data,
* calculate technical key figures,
* classify operating states,
* store data in a relational database,
* expose data through REST APIs,
* and later be containerized and deployed.

The project is intentionally not a generic tutorial app. It is designed around technical data, energy systems and asset monitoring scenarios.

---

## Current Version

**Current development focus:** `v0.7.1`

The current version focuses on:

* exposing PostgreSQL-backed station and measurement data through a FastAPI backend layer,
* providing REST endpoints for stations and measurements,
* using path parameters for station- and measurement-specific API calls,
* using query parameters for filtering and limiting API responses,
* validating path parameters, query parameters and JSON request bodies with FastAPI and Pydantic,
* returning proper HTTP errors for missing resources and invalid input data,
* defining typed API response schemas with Pydantic response models,
* accepting new measurement records through `POST /measurements`,
* writing new measurements to PostgreSQL with a parameterized `INSERT ... RETURNING` query,
* returning `201 Created` after successful measurement creation,
* retrieving individual measurement records through `GET /measurements/{measurement_id}`,
* updating measurement quality status through `PATCH /measurements/{measurement_id}`,
* using targeted `UPDATE ... RETURNING` statements for measurement quality updates,
* calculating global measurement KPI summaries through `GET /kpis/measurements`,
* calculating station-specific KPI summaries through `GET /stations/{station_id}/kpis`,
* excluding measurements with non-valid `quality_status` values from KPI calculations,
* adding automated API tests with pytest and FastAPI TestClient,
* checking successful responses, validation errors, not-found cases and write/read flows automatically,
* improving Swagger/OpenAPI documentation with API metadata, endpoint tags, summaries, descriptions and schemas,
* keeping the PostgreSQL workflow available as a terminal-based application flow,
* centralizing logging configuration,
* and continuing the separation of database access, API logic, output formatting and application flow.

The earlier CSV/OOP workflow from v0.3 is still preserved as a separate legacy demo.

---

## Current Features

The project currently supports three workflows:

### FastAPI backend workflow

* A FastAPI application is available in `src/api.py`.
* The API exposes station and measurement data as JSON responses.
* Station data is loaded from PostgreSQL through the existing database access layer.
* Measurement data is loaded from PostgreSQL through joined SQL queries.
* The API provides list endpoints, detail endpoints, write/update endpoints and KPI/analytics endpoints.
* Path parameters are used to retrieve station- and measurement-specific data.
* Query parameters can filter stations by type and limit measurement results.
* New measurement records can be created through `POST /measurements`.
* Existing measurement quality status values can be updated through `PATCH /measurements/{measurement_id}`.
* Global measurement KPIs can be retrieved through `GET /kpis/measurements`.
* Station-specific KPIs can be retrieved through `GET /stations/{station_id}/kpis`.
* KPI calculations currently include only measurements with `quality_status = "valid"`.
* Existing stations without valid measurements return KPI summaries with `measurement_count = 0` and nullable KPI values.
* Missing stations or measurements return proper `404 Not Found` responses.
* Invalid path parameters, query parameters and request body values are validated automatically by FastAPI and Pydantic.
* Pydantic request and response models define the expected API input and output structures.
* Automated API tests verify core endpoint behavior with pytest and FastAPI TestClient.
* The tests cover successful responses, empty filter results, `404 Not Found` cases, `422` validation errors, a create-then-read measurement flow and measurement quality status updates.
* The API uses custom OpenAPI metadata, endpoint tags, summaries, descriptions, response descriptions and schemas.
* Interactive API documentation is available through Swagger UI at `/docs`.

### Current PostgreSQL terminal workflow

* Station data is stored in a PostgreSQL `stations` table.
* Measurement data is stored in a PostgreSQL `measurements` table.
* Measurements are linked to stations through a foreign key.
* Python connects to PostgreSQL using `psycopg`.
* Database credentials are loaded from environment variables.
* Python reads station data from PostgreSQL.
* Python reads joined station and measurement data from PostgreSQL.
* Python reads individual measurement records by `measurement_id`.
* Python writes new measurement records to PostgreSQL.
* Python updates measurement quality status values in PostgreSQL.
* Python calculates KPI summaries from PostgreSQL measurement data.
* Raw PostgreSQL result rows are mapped into dictionaries with explicit field names.
* The terminal output shows a basic database report.

### Legacy CSV/OOP workflow

* Station data is read from a CSV file.
* Each CSV row is converted into a `Station` object.
* Valid load values are processed.
* Invalid or missing load values are handled through logging.
* Additional station data is imported from a simulated server source.
* Station reports are generated using object-oriented Python logic.

---

## Project Structure

```text
energy-operations-platform/
│
├── data/
│   └── stations.csv
│
├── demos/
│   ├── __init__.py
│   ├── database_test.py
│   └── legacy_csv_demo.py
│
├── docs/
│   └── database_notes.md
│
├── tests/
│   └── test_api.py
│
├── logs/
│   └── app.log              # generated locally, not committed
│
├── sql/
│   ├── schema.sql
│   ├── seed_data.sql
│   └── example_queries.sql
│
├── src/
│   ├── __init__.py
│   ├── api.py
│   ├── database.py
│   ├── logging_config.py
│   ├── main.py
│   ├── output.py
│   ├── read_documents.py
│   ├── schemas.py
│   ├── server.py
│   └── station.py
│
├── README.md
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## Module Responsibilities

| Path                       | Responsibility                                                             |
| -------------------------- | -------------------------------------------------------------------------- |
| `src/api.py`               | FastAPI application and REST endpoints for station and measurement data.   |
| `src/main.py`              | Terminal entry point for the PostgreSQL-based workflow.                    |
| `src/database.py`          | PostgreSQL connection management, read queries, measurement inserts, measurement quality updates and KPI queries. |
| `src/logging_config.py`    | Central logging configuration used by the application.                     |
| `src/output.py`            | Terminal output formatting for database report results.                    |
| `src/station.py`           | `Station` class and object-oriented station logic from earlier versions.   |
| `src/read_documents.py`    | CSV reading logic for the legacy CSV/OOP workflow.                         |
| `src/schemas.py`           | Pydantic request and response models that define API input and output structures. |
| `src/server.py`            | Simulated additional station data from a server source.                    |
| `tests/test_api.py`        | Automated FastAPI endpoint tests using pytest and TestClient.              |
| `demos/legacy_csv_demo.py` | Preserved v0.3 CSV/OOP workflow.                                           |
| `demos/database_test.py`   | Legacy direct PostgreSQL test script for learning/reference purposes.      |
| `sql/schema.sql`           | PostgreSQL table definitions.                                              |
| `sql/seed_data.sql`        | Example station and measurement data.                                      |
| `sql/example_queries.sql`  | Example SQL queries for filtering, joining and aggregating data.           |
| `data/stations.csv`        | Example CSV input data for the legacy workflow.                            |
| `docs/database_notes.md`   | Notes about the database model, SQL queries and Python integration.        |

---

## Technologies Used

* Python
* Object-oriented programming
* CSV processing
* Error handling
* Logging
* PostgreSQL
* SQL
* Relational data modeling
* Primary keys and foreign keys
* SQL joins and aggregations
* `psycopg`
* `python-dotenv`
* FastAPI
* Pydantic
* Uvicorn
* REST APIs
* JSON
* OpenAPI / Swagger UI
* FastAPI `Path` and `Query` parameter constraints
* FastAPI `response_model`
* Pydantic `BaseModel`
* Pydantic `Field`
* Python `Literal` types for constrained API values
* FastAPI request body validation
* HTTP `POST` and `201 Created`
* HTTP `PATCH` and `200 OK`
* SQL `INSERT ... RETURNING`
* SQL `UPDATE ... RETURNING`
* KPI/analytics queries
* Data-quality filtering with `quality_status`
* pytest
* FastAPI `TestClient`
* Git/GitHub project structure

---

## Database Model

The current PostgreSQL model contains two main tables:

### `stations`

Stores technical asset information.

Example fields:

* `station_id`
* `station_name`
* `station_type`
* `station_location`
* `created_at`

### `measurements`

Stores measurement values that belong to a station.

Example fields:

* `measurement_id`
* `station_id`
* `measurement_time`
* `load_value`
* `unit`
* `source`
* `quality_status`
* `created_at`

The relationship is:

```text
stations.station_id → measurements.station_id
```

One station can have many measurements.

---

## Environment Configuration

The real `.env` file is used locally and must not be committed.

Required environment variables:

```env
DB_NAME=energy_operations
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=5432
```

A safe template is provided in `.env.example`.

---

## How to Run

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the FastAPI backend

Run from the project root:

```bash
uvicorn src.api:app --reload
```

Open the interactive API documentation:

```text
http://localhost:8000/docs
```

The Swagger UI shows the custom API title, version, endpoint groups, parameter descriptions, response descriptions and Pydantic response schemas.

Example API URLs:

```text
http://localhost:8000/
http://localhost:8000/health
http://localhost:8000/stations
http://localhost:8000/stations?station_type=solar_park
http://localhost:8000/stations/1
http://localhost:8000/measurements
http://localhost:8000/measurements?limit=5
http://localhost:8000/measurements/1
PATCH http://localhost:8000/measurements/1
http://localhost:8000/kpis/measurements
http://localhost:8000/stations/1/kpis
http://localhost:8000/stations/1/measurements
http://localhost:8000/stations/1/measurements?limit=5
```

### Available API Endpoints

| Method | Endpoint                               | Description                                          |
| ------ | -------------------------------------- | ---------------------------------------------------- |
| `GET`  | `/`                                    | Returns a welcome message for the API.               |
| `GET`  | `/health`                             | Returns a basic API health check.                    |
| `GET`  | `/stations`                           | Returns all stations from PostgreSQL.                |
| `GET`  | `/stations?station_type=solar_park`   | Returns stations filtered by station type.           |
| `GET`  | `/stations/{station_id}`              | Returns one station by station ID.                   |
| `GET`  | `/measurements`                       | Returns joined station and measurement data.         |
| `GET`  | `/measurements?limit=5`               | Returns a limited number of measurement records.     |
| `GET`  | `/measurements/{measurement_id}`      | Returns one detailed measurement by measurement ID.  |
| `POST` | `/measurements`                       | Creates a new measurement record for an existing station. |
| `PATCH`| `/measurements/{measurement_id}`      | Updates the quality status of an existing measurement record. |
| `GET`  | `/kpis/measurements`                 | Returns global KPI summary values across all valid measurements. |
| `GET`  | `/stations/{station_id}/kpis`        | Returns KPI summary values for one specific station. |
| `GET`  | `/stations/{station_id}/measurements` | Returns measurements for one specific station.       |
| `GET`  | `/stations/{station_id}/measurements?limit=5` | Returns a limited number of measurements for one station. |

### API Query Parameters

| Endpoint | Query parameter | Example | Description |
| -------- | --------------- | ------- | ----------- |
| `/stations` | `station_type` | `/stations?station_type=solar_park` | Optional filter that returns only stations of the selected type. If no station matches, the API returns an empty list `[]`. |
| `/measurements` | `limit` | `/measurements?limit=5` | Optional limit for the number of returned measurement records. The value must be between `1` and `100`. |
| `/stations/{station_id}/measurements` | `limit` | `/stations/1/measurements?limit=5` | Optional limit for the number of returned measurement records for one station. The value must be between `1` and `100`. |

### API Request and Response Models

The API uses Pydantic models to define the expected input and output structures for station and measurement endpoints.

| Model | Used by | Purpose | Fields |
| ----- | ------- | ------- | ------ |
| `StationResponse` | `/stations`, `/stations/{station_id}` | Station API response model | `station_id`, `station_name`, `station_type`, `station_location` |
| `MeasurementResponse` | `/measurements`, `/stations/{station_id}/measurements` | Measurement overview response model with station name | `station_name`, `measurement_time`, `load_value`, `unit` |
| `MeasurementCreate` | `POST /measurements` | Request body model for creating new measurements | `station_id`, `measurement_time`, `load_value`, `unit`, `source`, `quality_status` |
| `MeasurementQualityUpdate` | `PATCH /measurements/{measurement_id}` | Request body model for updating measurement quality status | `quality_status` |
| `MeasurementDetailResponse` | `POST /measurements`, `/measurements/{measurement_id}`, `PATCH /measurements/{measurement_id}` | Detailed measurement response model | `measurement_id`, `station_id`, `measurement_time`, `load_value`, `unit`, `source`, `quality_status` |
| `MeasurementKPIsResponse` | `GET /kpis/measurements` | Global measurement KPI response model | `measurement_count`, `average_load`, `min_load`, `max_load`, `latest_measurement_time` |
| `StationKPIsResponse` | `GET /stations/{station_id}/kpis` | Station-specific KPI response model | `station_id`, `station_name`, `measurement_count`, `average_load`, `min_load`, `max_load`, `latest_measurement_time` |

The models are defined in `src/schemas.py` and connected to the FastAPI routes through request body type annotations and `response_model`.

This improves the API because:

* Swagger UI shows clear request and response schemas,
* FastAPI validates that returned data matches the declared API contract,
* incoming JSON request bodies are validated before database writes happen,
* response structures are easier to understand for external users,
* and automated tests can check API behavior against stable schemas.

`measurement_time` is returned in ISO 8601 date-time format, for example:

```json
"2026-06-22T08:15:00"
```

This is the standard JSON/API representation for date-time values.

### Create Measurement Request

New measurement records can be created with:

```text
POST /measurements
```

Example request body:

```json
{
  "station_id": 1,
  "measurement_time": "2026-07-02T08:15:00",
  "load_value": 123.45,
  "unit": "kW",
  "source": "manual_import",
  "quality_status": "valid"
}
```

Validation rules for `MeasurementCreate` currently include:

| Field | Validation |
| ----- | ---------- |
| `station_id` | Must be an integer greater than or equal to `1`. |
| `measurement_time` | Must be a valid date-time value. |
| `load_value` | Must be greater than or equal to `0`. |
| `unit` | Must be one of the allowed units, currently `kW` or `MW`. |
| `source` | Must be a non-empty string. |
| `quality_status` | Must be one of `valid`, `invalid` or `estimated`. |

A successful request returns:

```text
201 Created
```

with the created measurement record including the database-generated `measurement_id`.

### Update Measurement Quality Status Request

Measurement quality status can be updated with:

```text
PATCH /measurements/{measurement_id}
```

Example request body:

```json
{
  "quality_status": "invalid"
}
```

Allowed values for `quality_status` are currently:

```text
valid
invalid
estimated
```

A successful request returns:

```text
200 OK
```

with the updated detailed measurement record.

This endpoint is used to mark a measurement as valid, invalid or estimated without deleting the measurement record. This is intentionally closer to realistic measurement-data workflows than immediately removing technical history from the database.

### KPI Summary Endpoints

Global measurement KPI values can be retrieved with:

```text
GET /kpis/measurements
```

Station-specific KPI values can be retrieved with:

```text
GET /stations/{station_id}/kpis
```

The KPI responses currently include:

| Field | Meaning |
| ----- | ------- |
| `measurement_count` | Number of valid measurement records used for the calculation. |
| `average_load` | Average load value across valid measurements. |
| `min_load` | Minimum load value across valid measurements. |
| `max_load` | Maximum load value across valid measurements. |
| `latest_measurement_time` | Latest timestamp among valid measurements. |

The station-specific endpoint also includes:

```text
station_id
station_name
```

KPI calculations currently include only measurements with:

```text
quality_status = "valid"
```

Measurements marked as `invalid` or `estimated` are excluded from KPI calculations. This makes the analytics layer depend on the data-quality status instead of blindly aggregating all raw measurement records.

If a station exists but has no valid measurements, the station-specific KPI endpoint returns:

```text
200 OK
measurement_count = 0
average_load = null
min_load = null
max_load = null
latest_measurement_time = null
```


### API Documentation

The FastAPI application includes custom OpenAPI metadata for a clearer portfolio presentation.

Current API documentation features:

| Feature | Purpose |
| ------- | ------- |
| API title | Shows the project-specific API name in Swagger UI. |
| API description | Explains the purpose of the Energy Operations Platform API. |
| API version | Documents the current API version, currently `0.7.1`. |
| Endpoint tags | Groups routes into `General`, `Stations`, `Measurements` and `KPIs`. |
| Endpoint summaries | Make the route overview easier to scan. |
| Endpoint descriptions | Explain what each route returns and how it should be used. |
| Parameter descriptions | Explain path and query parameters directly in Swagger UI. |
| Response descriptions | Describe the returned response type in the generated API documentation. |
| Request and response schemas | Show station, measurement and KPI request/response models as typed API schemas. |

### API Error Behavior

| Request example                         | Result                                                            |
| --------------------------------------- | ----------------------------------------------------------------- |
| `/stations/1`                           | Returns station with ID `1`.                                      |
| `/stations/999`                         | Returns `404 Not Found` if the station does not exist.             |
| `/stations/abc`                         | Returns a validation error because `station_id` must be an integer. |
| `/stations/0`                           | Returns a validation error because `station_id` must be at least `1`. |
| `/stations?station_type=unknown`        | Returns an empty list `[]` because the filter has no matches.      |
| `/measurements?limit=5`                 | Returns the first five joined measurement records.                 |
| `/measurements?limit=0`                 | Returns a validation error because `limit` must be at least `1`.   |
| `/measurements?limit=101`               | Returns a validation error because `limit` must be at most `100`.  |
| `/measurements?limit=abc`               | Returns a validation error because `limit` must be an integer.     |
| `/measurements/1`                       | Returns one detailed measurement record with ID `1`.              |
| `/measurements/999999999`               | Returns `404 Not Found` if the measurement does not exist.         |
| `/measurements/0`                       | Returns a validation error because `measurement_id` must be at least `1`. |
| `/measurements/abc`                     | Returns a validation error because `measurement_id` must be an integer. |
| `POST /measurements` with valid body    | Creates a new measurement and returns `201 Created`.              |
| `POST /measurements` with unknown `station_id` | Returns `404 Not Found` if the station does not exist.      |
| `POST /measurements` with invalid body  | Returns a validation error, for example for negative load values or invalid quality status. |
| `PATCH /measurements/1` with valid body | Updates the measurement quality status and returns `200 OK`. |
| `PATCH /measurements/999999` | Returns `404 Not Found` if the measurement does not exist. |
| `PATCH /measurements/abc` | Returns a validation error because `measurement_id` must be an integer. |
| `PATCH /measurements/1` with invalid body | Returns a validation error, for example for missing or invalid `quality_status`. |
| `/kpis/measurements`                    | Returns global KPI values across valid measurements.               |
| `/stations/1/kpis`                      | Returns KPI values for station `1` based on valid measurements.    |
| `/stations/9/kpis`                      | Returns `200 OK` with `measurement_count = 0` and nullable KPI values if station `9` exists but has no valid measurements. |
| `/stations/999999/kpis`                 | Returns `404 Not Found` if the station does not exist.             |
| `/stations/0/kpis`                      | Returns a validation error because `station_id` must be at least `1`. |
| `/stations/abc/kpis`                    | Returns a validation error because `station_id` must be an integer. |
| `/stations/1/measurements`              | Returns all measurements for station `1`.                         |
| `/stations/1/measurements?limit=5`       | Returns at most five measurements for station `1`.                 |
| `/stations/1/measurements?limit=0`       | Returns a validation error because `limit` must be at least `1`.   |
| `/stations/999/measurements`            | Returns `404 Not Found` if the station does not exist.             |
| `/stations/abc/measurements`            | Returns a validation error because `station_id` must be an integer. |

### Automated API Tests

The project includes automated API tests for the current FastAPI endpoints.

The tests are located in:

```text
tests/test_api.py
```

Run the tests from the project root:

```bash
py -m pytest -v
```

Current test scope:

| Area | Tested behavior |
| ---- | --------------- |
| General endpoints | `/` and `/health` return `200 OK` and the expected JSON responses. |
| Station list endpoint | `/stations` returns a list with the expected station fields. |
| Station filtering | `/stations?station_type=unknown` returns an empty list `[]`. |
| Station detail endpoint | `/stations/1` returns one station object. |
| Station errors | Non-existing IDs return `404`; invalid path parameters return `422`. |
| Measurement list endpoint | `/measurements` returns a list with the expected measurement fields. |
| Measurement limiting | `/measurements?limit=5` returns at most five records. |
| Measurement validation | Invalid `limit` values return `422`. |
| Measurement creation | `POST /measurements` creates a new measurement and returns `201 Created`. |
| Measurement creation errors | Unknown stations return `404`; invalid request bodies return `422`. |
| Measurement detail endpoint | `/measurements/{measurement_id}` returns one detailed measurement record. |
| Measurement detail errors | Non-existing measurement IDs return `404`; invalid IDs return `422`. |
| Measurement write/read flow | A test creates a measurement and then retrieves it again by `measurement_id`. |
| Measurement quality update | `PATCH /measurements/{measurement_id}` updates `quality_status` and returns `200 OK`. |
| Measurement quality update errors | Missing, invalid or wrong-typed `quality_status` values return `422`; unknown measurement IDs return `404`. |
| Nested station measurements | `/stations/1/measurements` returns measurements for one station. |
| Nested endpoint errors | Missing stations return `404`; invalid station IDs or limits return `422`. |
| Global KPI summary | `/kpis/measurements` returns global KPI fields across valid measurements. |
| Station KPI summary | `/stations/{station_id}/kpis` returns station-specific KPI fields. |
| Station KPI edge cases | Existing stations without valid measurements return `200 OK` with empty KPI values; unknown stations return `404`; invalid station IDs return `422`. |

The tests currently use the local PostgreSQL database and the existing seed data. A separate test database or dependency overrides can be introduced later when the project structure becomes more advanced.

### Run the current PostgreSQL terminal workflow

Run from the project root:

```bash
python -m src.main
```

This starts the current PostgreSQL terminal workflow:

1. Load station and measurement data from PostgreSQL.
2. Print station data.
3. Print joined measurement data.
4. Write technical runtime information to the local log file.

### Run the legacy CSV/OOP workflow

Run from the project root:

```bash
python -m demos.legacy_csv_demo
```

This runs the previous CSV-based workflow:

1. Read station data from `data/stations.csv`.
2. Convert rows into `Station` objects.
3. Import additional simulated server data.
4. Generate station reports.

---

## SQL Files

The SQL files are stored in the `sql/` directory.

| File                      | Purpose                                            |
| ------------------------- | -------------------------------------------------- |
| `sql/schema.sql`          | Creates the `stations` and `measurements` tables.  |
| `sql/seed_data.sql`       | Inserts example stations and measurements.         |
| `sql/example_queries.sql` | Contains example queries for learning and testing. |

Covered SQL concepts include:

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

---

## Logging

The project uses Python logging to make program behavior and data-quality issues traceable.

Examples of logged events:

| Situation                   | Log Level |
| --------------------------- | --------- |
| Program started             | `INFO`    |
| API endpoint called         | `INFO`    |
| Database connection started | `INFO`    |
| Database query executed     | `DEBUG`   |
| Database connection closed  | `INFO`    |
| Missing load value          | `WARNING` |
| Invalid load value          | `WARNING` |
| Resource not found          | `WARNING` |
| File not found              | `ERROR`   |

The log file `logs/app.log` is generated locally and should not be committed.

---

## Version History

| Version | Description                                                                                                                 |
| ------- | --------------------------------------------------------------------------------------------------------------------------- |
| `v0.1`  | First Python script with station data stored directly in code. Basic calculations and classification.                       |
| `v0.2`  | External data sources introduced. Station data loaded from text/CSV files. Basic error handling added.                      |
| `v0.3`  | First object-oriented structure with a `Station` class. CSV rows are converted into station objects.                        |
| `v0.31` | Refactoring of CSV conversion into `Station.from_csv_row()`. More robust handling of invalid and missing load values.       |
| `v0.32` | Basic logging introduced. Program flow and data-quality issues are written to `app.log`.                                    |
| `v0.4`  | PostgreSQL integration added. SQL schema, seed data, example queries, Python database connection and project restructuring. |
| `v0.4.1`| Database query results are mapped from raw PostgreSQL rows into dictionaries with explicit field names as preparation for JSON and FastAPI responses. |
| `v0.5`  | FastAPI backend layer added. PostgreSQL-backed station and measurement data is exposed through REST endpoints as JSON, including path and query parameters. |
| `v0.5.1`| API documentation polish. FastAPI metadata, endpoint tags, summaries, descriptions, response descriptions and parameter constraints are improved for Swagger/OpenAPI. |
| `v0.5.2`| Pydantic response models added. Station and measurement endpoints now use typed response schemas through FastAPI `response_model`. |
| `v0.5.3`| Automated API tests added with pytest and FastAPI TestClient for success cases, validation errors, not-found responses, query parameters and nested station measurement endpoints. |
| `v0.6.0`| First write endpoint added. `POST /measurements` accepts validated JSON request bodies, writes new measurement records to PostgreSQL and returns `201 Created`. |
| `v0.6.1`| Measurement creation validation added with Pydantic `Field` constraints and `Literal` values for units and quality status. |
| `v0.6.2`| Measurement detail endpoint added. `GET /measurements/{measurement_id}` retrieves one full measurement record by ID and is covered by automated tests. |
| `v0.6.3`| Measurement quality status update endpoint added. `PATCH /measurements/{measurement_id}` updates `quality_status` for existing measurements and is covered by automated tests. |
| `v0.7.0`| Global KPI endpoint added. `GET /kpis/measurements` returns aggregated KPI values across valid measurement records. |
| `v0.7.1`| Station-specific KPI endpoint added. `GET /stations/{station_id}/kpis` returns KPI values for one station and handles stations without valid measurements. |

---

## Learning Goals Covered So Far

The current project demonstrates practical knowledge in:

* Python basics,
* functions and return values,
* modules and imports,
* object-oriented programming,
* class methods,
* special methods such as `__str__` and `__repr__`,
* CSV processing,
* validation of external input data,
* defensive programming,
* logging,
* relational database design,
* SQL queries and aggregations,
* KPI calculations with `COUNT`, `AVG`, `MIN`, `MAX` and latest timestamp values,
* PostgreSQL setup,
* Python-to-PostgreSQL access,
* environment-based configuration,
* mapping database query results into Python dictionaries,
* separation of responsibilities between files,
* REST API basics,
* FastAPI routing,
* JSON responses,
* path parameters,
* query parameters,
* parameter constraints with FastAPI `Query`,
* path constraints with FastAPI `Path`,
* API metadata and endpoint documentation with FastAPI,
* Pydantic response models,
* typed API response schemas,
* FastAPI `response_model`,
* FastAPI request body models,
* Pydantic `Field` validation,
* constrained values with `Literal`,
* HTTP `POST` endpoints,
* `201 Created` responses,
* PostgreSQL `INSERT ... RETURNING`,
* PostgreSQL `UPDATE ... RETURNING`,
* HTTP `PATCH` endpoints,
* updating existing resources,
* calculating global and station-specific KPI summaries,
* filtering analytics by measurement data quality,
* reading individual resources by ID,
* pytest basics,
* FastAPI `TestClient`,
* automated API endpoint tests,
* testing successful responses and expected error cases,
* testing create-and-read API flows,
* HTTP status codes,
* automatic request validation,
* and automatic API documentation with OpenAPI / Swagger UI.

---

## Roadmap

Next planned steps:

* Finalize the v0.7 KPI/analytics documentation and release tag.
* Improve database error handling.
* Introduce routers when the number of endpoints grows further.
* Improve the PostgreSQL access layer step by step.
* Plan a better test data strategy, for example fixtures or a separate test database.
* Add Docker setup.
* Add basic cloud deployment preparation.
* Add monitoring and security basics.
