# Energy Operations Platform

## Overview

The **Energy Operations Platform** is a Python-based backend and data project for processing, validating and analyzing technical energy and station data.

The project started with CSV-based station data and object-oriented Python logic. The current development focus is the transition toward a PostgreSQL-backed data backend with relational station and measurement data.

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

**Current development focus:** `v0.4`

The current version focuses on:

* PostgreSQL integration,
* a relational data model with `stations` and `measurements`,
* SQL queries with `JOIN`, `WHERE`, `GROUP BY` and `HAVING`,
* Python database access using `psycopg`,
* environment-based database configuration with `.env`,
* mapping PostgreSQL result rows into dictionaries with explicit field names,
* separation of database access, output formatting and application flow,
* and a reorganized project structure.

The earlier CSV/OOP workflow from v0.3 is still preserved as a separate legacy demo.

---

## Current Features

The project currently supports two workflows:

### Current PostgreSQL workflow

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
├── sql/
│   ├── schema.sql
│   ├── seed_data.sql
│   └── example_queries.sql
│
├── src/
│   ├── __init__.py
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

## Module Responsibilities

| Path                       | Responsibility                                                           |
| -------------------------- | ------------------------------------------------------------------------ |
| `src/main.py`              | Current application entry point for the PostgreSQL-based v0.4 workflow.  |
| `src/database.py`          | PostgreSQL connection management and read queries.                       |
| `src/output.py`            | Terminal output formatting for database report results.                  |
| `src/station.py`           | `Station` class and object-oriented station logic from earlier versions. |
| `src/read_documents.py`    | CSV reading logic for the legacy CSV/OOP workflow.                       |
| `src/server.py`            | Simulated additional station data from a server source.                  |
| `demos/legacy_csv_demo.py` | Preserved v0.3 CSV/OOP workflow.                                         |
| `demos/database_test.py`   | Legacy direct PostgreSQL test script for learning/reference purposes.    |
| `sql/schema.sql`           | PostgreSQL table definitions.                                            |
| `sql/seed_data.sql`        | Example station and measurement data.                                    |
| `sql/example_queries.sql`  | Example SQL queries for filtering, joining and aggregating data.         |
| `data/stations.csv`        | Example CSV input data for the legacy workflow.                          |
| `docs/database_notes.md`   | Notes about the database model, SQL queries and Python integration.      |

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

### Run the current PostgreSQL workflow

Run from the project root:

```bash
python -m src.main
```

This starts the current v0.4 workflow:

1. Load station and measurement data from PostgreSQL.
2. Print station data.
3. Print joined measurement data.
4. Write technical runtime information to `app.log`.

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
| Database connection started | `INFO`    |
| Database query executed     | `DEBUG`   |
| CSV file opened             | `INFO`    |
| Missing load value          | `WARNING` |
| Invalid load value          | `WARNING` |
| File not found              | `ERROR`   |

The log file `app.log` is generated locally and should not be committed.

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
* and separation of responsibilities between files.

---

## Roadmap

Next planned steps:

* Improve the PostgreSQL access layer step by step.
* Add more realistic database queries and KPIs.
* Convert database rows into cleaner Python data structures.
* Add first FastAPI endpoints.
* Return station and measurement data as JSON.
* Add basic tests.
* Add Docker setup.
* Add basic cloud deployment preparation.
* Add monitoring and security basics.
