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

**Current development focus:** `v0.5.2`

The current version focuses on:

* exposing PostgreSQL-backed station and measurement data through a FastAPI backend layer,
* providing REST endpoints for stations and measurements,
* using path parameters for station-specific API calls,
* using query parameters for filtering and limiting API responses,
* validating path and query parameters with FastAPI constraints,
* returning proper HTTP errors for missing resources,
* defining typed API response schemas with Pydantic response models,
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
* The API provides list endpoints and detail endpoints.
* Path parameters are used to retrieve station-specific data.
* Query parameters can filter stations by type and limit measurement results.
* Missing stations return a proper `404 Not Found` response.
* Invalid path and query parameter values are validated automatically by FastAPI.
* Pydantic response models define the expected API response structures.
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
| `src/database.py`          | PostgreSQL connection management and read queries.                         |
| `src/logging_config.py`    | Central logging configuration used by the application.                     |
| `src/output.py`            | Terminal output formatting for database report results.                    |
| `src/station.py`           | `Station` class and object-oriented station logic from earlier versions.   |
| `src/read_documents.py`    | CSV reading logic for the legacy CSV/OOP workflow.                         |
| `src/schemas.py`           | Pydantic response models that define the public API response structures.   |
| `src/server.py`            | Simulated additional station data from a server source.                    |
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
http://localhost:8000/stations/1/measurements
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
| `GET`  | `/stations/{station_id}/measurements` | Returns measurements for one specific station.       |

### API Query Parameters

| Endpoint | Query parameter | Example | Description |
| -------- | --------------- | ------- | ----------- |
| `/stations` | `station_type` | `/stations?station_type=solar_park` | Optional filter that returns only stations of the selected type. If no station matches, the API returns an empty list `[]`. |
| `/measurements` | `limit` | `/measurements?limit=5` | Optional limit for the number of returned measurement records. The value must be between `1` and `100`. |

### API Response Models

The API uses Pydantic response models to define the expected response structures for station and measurement endpoints.

| Model | Used by | Fields |
| ----- | ------- | ------ |
| `StationResponse` | `/stations`, `/stations/{station_id}` | `station_id`, `station_name`, `station_type`, `station_location` |
| `MeasurementResponse` | `/measurements`, `/stations/{station_id}/measurements` | `station_name`, `measurement_time`, `load_value`, `unit` |

The response models are defined in `src/schemas.py` and connected to the FastAPI routes through `response_model`.

This improves the API because:

* Swagger UI shows clear response schemas,
* FastAPI validates that returned data matches the declared API contract,
* response structures are easier to understand for external users,
* and later tests can check API behavior against stable schemas.

`measurement_time` is returned in ISO 8601 date-time format, for example:

```json
"2026-06-22T08:15:00"
```

This is the standard JSON/API representation for date-time values.

### API Documentation

The FastAPI application includes custom OpenAPI metadata for a clearer portfolio presentation.

Current API documentation features:

| Feature | Purpose |
| ------- | ------- |
| API title | Shows the project-specific API name in Swagger UI. |
| API description | Explains the purpose of the Energy Operations Platform API. |
| API version | Documents the current API version, currently `0.5.2`. |
| Endpoint tags | Groups routes into `General`, `Stations` and `Measurements`. |
| Endpoint summaries | Make the route overview easier to scan. |
| Endpoint descriptions | Explain what each route returns and how it should be used. |
| Parameter descriptions | Explain path and query parameters directly in Swagger UI. |
| Response descriptions | Describe the returned response type in the generated API documentation. |
| Response schemas | Show `StationResponse` and `MeasurementResponse` as typed API response models. |

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
| `/stations/1/measurements`              | Returns all measurements for station `1`.                         |
| `/stations/999/measurements`            | Returns `404 Not Found` if the station does not exist.             |

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
* HTTP status codes,
* automatic request validation,
* and automatic API documentation with OpenAPI / Swagger UI.

---

## Roadmap

Next planned steps:

* Add automated API tests for the existing FastAPI endpoints.
* Add more realistic database queries and KPIs.
* Introduce routers later when the number of endpoints grows.
* Improve the PostgreSQL access layer step by step.
* Add Docker setup.
* Add basic cloud deployment preparation.
* Add monitoring and security basics.
