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

## Next Steps

Planned next steps:

* define the first SQL table structure
* create a `schema.sql` file
* practice basic SQL commands
* prepare PostgreSQL integration
* later connect the Python project to a database