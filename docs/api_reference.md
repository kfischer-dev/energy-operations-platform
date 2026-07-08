# API Reference

This document describes the current REST API surface of the Energy Operations Platform.

For database implementation details, see [`database_notes.md`](database_notes.md).  
For test coverage and test data handling, see [`test_strategy.md`](test_strategy.md).

## API Base

Local development server:

```text
http://127.0.0.1:8000
```

Interactive OpenAPI documentation:

```text
http://127.0.0.1:8000/docs
```

## General Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Returns a public API welcome message |
| `GET` | `/health` | Returns a lightweight API health status |

## Station Endpoints

### `GET /stations`

Returns all stations.

Optional query parameter:

| Parameter | Type | Rule | Purpose |
|---|---|---|---|
| `station_type` | string | optional | Filter stations by type, for example `solar_park` or `wind_park` |

Example:

```text
GET /stations?station_type=solar_park
```

### `GET /stations/{station_id}`

Returns one station by ID.

| Parameter | Type | Rule |
|---|---|---|
| `station_id` | integer | must be `>= 1` |

Expected behavior:

- `200 OK` if the station exists
- `404 Not Found` if the station ID is valid but unknown
- `422 Unprocessable Entity` if the path parameter is invalid, for example `0` or `abc`

## Measurement Endpoints

### `GET /measurements`

Returns joined measurement data with station names.

Optional query parameter:

| Parameter | Type | Rule | Purpose |
|---|---|---|---|
| `limit` | integer | `1 <= limit <= 100` | Restrict number of returned measurements |

Example:

```text
GET /measurements?limit=5
```

### `GET /stations/{station_id}/measurements`

Returns all measurements for one station.

| Parameter | Type | Rule |
|---|---|---|
| `station_id` | integer | must be `>= 1` |
| `limit` | integer | optional, `1 <= limit <= 100` |

Expected behavior:

- `200 OK` if the station exists
- `404 Not Found` if the station ID is valid but unknown
- `422 Unprocessable Entity` for invalid path or query parameters

### `GET /measurements/{measurement_id}`

Returns one detailed measurement record by ID.

| Parameter | Type | Rule |
|---|---|---|
| `measurement_id` | integer | must be `>= 1` |

Expected behavior:

- `200 OK` if the measurement exists
- `404 Not Found` if the measurement ID is valid but unknown
- `422 Unprocessable Entity` for invalid path parameters

### `POST /measurements`

Creates a new measurement for an existing station.

Request body:

```json
{
  "station_id": 8,
  "measurement_time": "2026-07-02T08:15:00",
  "load_value": 105.25,
  "unit": "kW",
  "source": "pytest",
  "quality_status": "valid"
}
```

Validation rules:

| Field | Rule |
|---|---|
| `station_id` | integer, `>= 1`, must reference an existing station |
| `measurement_time` | valid datetime |
| `load_value` | number, `>= 0` |
| `unit` | `kW` or `MW` |
| `source` | non-empty string |
| `quality_status` | `valid`, `invalid` or `estimated` |

Expected behavior:

- `201 Created` if the measurement is stored successfully
- `404 Not Found` if the station ID is valid but unknown
- `422 Unprocessable Entity` for invalid request bodies

### `PATCH /measurements/{measurement_id}`

Updates the `quality_status` of an existing measurement.

Request body:

```json
{
  "quality_status": "invalid"
}
```

Validation rules:

| Field | Rule |
|---|---|
| `quality_status` | `valid`, `invalid` or `estimated` |

Expected behavior:

- `200 OK` if the measurement is updated successfully
- `404 Not Found` if the measurement ID is valid but unknown
- `422 Unprocessable Entity` for invalid path parameters or request bodies

## KPI Endpoints

### `GET /kpis/measurements`

Returns a global KPI summary over all valid measurements.

The endpoint calculates:

- `measurement_count`
- `average_load`
- `min_load`
- `max_load`
- `latest_measurement_time`

Important rule:

```text
Only measurements with quality_status = 'valid' are included.
```

### `GET /stations/{station_id}/kpis`

Returns a KPI summary for one station.

| Parameter | Type | Rule |
|---|---|---|
| `station_id` | integer | must be `>= 1` |

Expected behavior:

- `200 OK` with KPI values if the station exists and has valid measurements
- `200 OK` with `measurement_count = 0` and nullable KPI values if the station exists but has no valid measurements
- `404 Not Found` if the station ID is valid but unknown
- `422 Unprocessable Entity` for invalid path parameters

## Response Models

| Model | Used by |
|---|---|
| `StationResponse` | Station endpoints |
| `MeasurementResponse` | Measurement list endpoints |
| `MeasurementDetailResponse` | Measurement create/read/update detail endpoints |
| `MeasurementKPIsResponse` | Global KPI endpoint |
| `StationKPIsResponse` | Station-specific KPI endpoint |

## Error Behavior Summary

| Status | Meaning | Example |
|---|---|---|
| `200 OK` | Valid request and successful read/update | Existing station or KPI request |
| `201 Created` | Valid request and successful creation | `POST /measurements` |
| `404 Not Found` | Request shape is valid, but resource does not exist | `/stations/9999` |
| `422 Unprocessable Entity` | Request path, query parameter or body is invalid | `/stations/abc`, `limit=0`, invalid `quality_status` |

## Not-found Handling

Expected resource-not-found cases are handled consistently in the API layer.

Current helper functions in `src/api.py`:

| Helper | Purpose |
|---|---|
| `get_station_or_404(conn, station_id)` | Loads one station or raises `404 Not Found` |
| `get_measurement_or_404(conn, measurement_id)` | Loads one measurement or raises `404 Not Found` |

These helpers centralize repeated station and measurement existence checks. Endpoints can therefore focus on their main API task instead of repeating the same fetch-and-404 logic.

Current 404 response style:

```json
{
  "detail": "Station with id 9999 not found"
}
```

```json
{
  "detail": "Measurement with id 99999999 not found"
}
```

Validation errors remain handled by FastAPI and Pydantic as `422 Unprocessable Entity`.

## Current API Limitations

- Routes are still kept in `src/api.py`; router modules can be introduced later.
- Expected station and measurement 404 cases are centralized through small API helper functions.
- Database connection errors are not yet handled through central exception handlers.
- Authentication and API keys are not implemented yet.
- Delete endpoints are not implemented yet.
