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

Possible fields:

* id
* name
* station_type
* location
* created_at

Example:

| id | name | station_type | location |
|---:|---|---|---|
| 1 | Station A | solar_park | Stuttgart |
| 2 | Station B | wind_park | Ulm |

## Table: measurements

The measurements table stores changing measurement values.

Possible fields:

* id
* station_id
* timestamp
* load_kw
* unit
* source
* quality_status
* created_at

Example:

| id | station_id | timestamp | load_kw | unit |
|---:|---:|---|---:|---|
| 1 | 1 | 2026-06-22 08:00 | 80 | kW |
| 2 | 1 | 2026-06-22 08:15 | 95 | kW |
| 3 | 1 | 2026-06-22 08:30 | 120 | kW |

## Primary Key and Foreign Key

Each station has a unique `id`.

Each measurement also has a unique `id`.

The field `station_id` in the `measurements` table refers to the `id` of the related station.

This creates a relationship:

* stations.id → measurements.station_id

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

stations.id → measurements.station_id

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

### Current Focus

- Separate the SQL work into clean project files:
  - `schema.sql` for table definitions
  - `seed_data.sql` for example data
  - `example_queries.sql` for test queries
- Test the foreign key constraint with an invalid `station_id`.
- Keep the database model small and understandable before connecting it to Python.

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

### Next Steps

- Finalize the first PostgreSQL schema.
- Keep schema, seed data and example queries in separate SQL files.
- Extend example queries for common energy KPIs.
- Test and document the foreign key constraint.
- Prepare the Python database connection.
- Later connect the existing Python project to PostgreSQL.