# API Reference

## Purpose

This document describes the public REST API contract of the Energy Operations Platform for `v0.11.1`.

Interactive OpenAPI documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## API Base

Default local URL:

```text
http://127.0.0.1:8000
```

All request and response bodies use JSON. Date-time values are serialized as ISO 8601 timestamps.

## `v0.11.1` Measurement Model

`v0.11.1` makes point-in-time active power the canonical public measurement contract.

Raw measurement requests/responses no longer include:

```text
interval_minutes
energy_kwh
```

Energy is derived by period-based KPI/aggregation logic rather than persisted redundantly. `simulation_runs.interval_minutes` remains part of simulation configuration.

There is no public simulation endpoint in `v0.11.1`.

---

# General Endpoints

## `GET /`

Returns a basic welcome message.

```json
{
  "message": "Energy Operations Platform API"
}
```

## `GET /health`

Lightweight application health endpoint.

```json
{
  "status": "ok"
}
```

The endpoint confirms that FastAPI is running. It does not query PostgreSQL.

---

# Asset Endpoints

## `GET /assets`

Returns compact asset records using `AssetSummaryResponse`.

Optional query parameter:

| Parameter | Type | Rules | Description |
|---|---|---|---|
| `asset_type` | string | optional | Exact filter such as `solar_park`, `wind_park` or `battery_storage` |

Example response item:

```json
{
  "asset_id": 1,
  "asset_name": "North Sea Wind Park",
  "asset_code": "N-WIND-001",
  "asset_location": "North Sea",
  "asset_role": "producer",
  "asset_type": "wind_park",
  "region_code": "DE-NORTH",
  "rated_power_kw": 120000.0,
  "operating_status": "online"
}
```

An unknown `asset_type` filter returns an empty list.

## `GET /assets/{asset_id}`

Returns one complete asset using `AssetResponse`.

Path parameter:

| Parameter | Type | Rules |
|---|---|---|
| `asset_id` | integer | `>= 1` |

Example response:

```json
{
  "asset_id": 1,
  "asset_name": "North Sea Wind Park",
  "asset_code": "N-WIND-001",
  "asset_location": "North Sea",
  "asset_role": "producer",
  "asset_type": "wind_park",
  "region_id": 1,
  "region_code": "DE-NORTH",
  "region_name": "Northern Germany",
  "rated_power_kw": 120000.0,
  "latitude": 54.5,
  "longitude": 7.5,
  "operating_status": "online"
}
```

Unknown assets return `404 Not Found`.

---

# Measurement Endpoints

## Summary versus detail contracts

Measurement list endpoints use a compact response. Detail, POST and PATCH endpoints use the complete response contract.

### `MeasurementSummaryResponse`

```text
measurement_id
asset_id
asset_code
asset_name
measurement_time
active_power_kw
quality_status
```

### `MeasurementResponse`

```text
measurement_id
asset_id
asset_code
asset_name
asset_type
asset_role
region_code
measurement_time
active_power_kw
source
quality_status
```

Allowed quality values:

```text
valid
invalid
estimated
```

## `GET /measurements`

Returns measurement summaries across all assets.

Optional query parameter:

| Parameter | Type | Rules |
|---|---|---|
| `limit` | integer | optional, `1` to `100` |

## `GET /assets/{asset_id}/measurements`

Returns measurement summaries for one asset.

| Parameter | Location | Type | Rules |
|---|---|---|---|
| `asset_id` | path | integer | `>= 1` |
| `limit` | query | integer | optional, `1` to `100` |

The parent asset is checked first:

- known asset without measurements → `200 OK` with `[]`
- unknown asset → `404 Not Found`

## `GET /measurements/{measurement_id}`

Returns one complete point-in-time measurement.

Path parameter:

| Parameter | Type | Rules |
|---|---|---|
| `measurement_id` | integer | `>= 1` |

Unknown measurement IDs return `404 Not Found`.

## `POST /measurements`

Creates one point-in-time active-power measurement for an existing asset.

Required body:

```json
{
  "asset_id": 1,
  "measurement_time": "2026-07-02T08:15:00+02:00",
  "active_power_kw": 82000.0,
  "source": "manual_import",
  "quality_status": "valid"
}
```

Validation includes:

- `asset_id >= 1`
- `source` must not be empty
- `quality_status` must be `valid`, `invalid` or `estimated`

Successful creation returns `201 Created` and the complete `MeasurementResponse`.

Unknown parent assets return `404 Not Found`.

## `PATCH /measurements/{measurement_id}`

Updates only `quality_status`.

```json
{
  "quality_status": "estimated"
}
```

Successful update returns the complete `MeasurementResponse` with `200 OK`.

---

# KPI Endpoints

Both KPI endpoints are period based and require ISO-8601 `start_time` and `end_time` query parameters.

Common KPI fields:

```text
period_start
period_end
measurement_count
avg_active_power_kw
min_measured_power_kw
max_measured_power_kw
total_energy_kwh
coverage_ratio
```

Field semantics:

- `measurement_count` counts valid measured points inside the requested period,
- `min_measured_power_kw` / `max_measured_power_kw` use measured in-period points only,
- `avg_active_power_kw` is time weighted over the reconstructed curve,
- `total_energy_kwh` is derived with trapezoidal integration,
- `coverage_ratio` is covered duration divided by requested duration.

Boundary measurements immediately before/after the requested period may be loaded for interpolation. They contribute to derived average/energy/coverage but do not increase measured count or measured min/max values.

Only `quality_status = valid` participates in the current KPI calculation. `invalid` and `estimated` rows are excluded.

## `GET /kpis/measurements`

Returns the global period KPI summary.

Measurements are grouped by asset before energy integration so segments are never built between different assets. Asset-level results are then combined into the global response.

The database query retrieves the requested period plus only the nearest required support measurements per asset. It uses PostgreSQL `DISTINCT ON` and exact-boundary checks to avoid duplicate support rows when the requested boundary already exists as a measurement.

## `GET /assets/{asset_id}/kpis`

Returns the same period KPI semantics scoped to one asset and additionally includes:

```text
asset_id
asset_name
```

Behavior:

- unknown asset → `404 Not Found`
- existing asset without usable measurements → zero count/coverage and nullable derived values
- one valid in-period point can define measured min/max/count but cannot define energy by itself

---

# Simulation Service in `v0.11.1`

Simulation is **not exposed as a REST endpoint** yet.

The internal service flow is:

```text
create simulation_run
→ commit run metadata
→ mark running
→ commit status
→ load registry-supported database assets
→ simulate point-in-time PowerMeasurements
→ batch insert measurements
→ derive PowerIntervalDrafts in memory
→ validate complete intervals
→ mark completed and persist generated_measurement_count
→ commit
```

Failure path:

```text
simulation or insert error
→ rollback generated measurements
→ mark simulation_run failed
→ commit failed status
→ re-raise original exception
```

The integration suite verifies both paths against PostgreSQL.

---

# HTTP and Validation Behavior

Common behavior:

| Scenario | Result |
|---|---|
| Valid GET | `200 OK` |
| Valid POST | `201 Created` |
| Missing asset/measurement | `404 Not Found` |
| Invalid path/query/body input | `422 Unprocessable Entity` |
| Empty asset measurement list | `200 OK`, `[]` |

Path IDs use `ge=1`. Measurement list limits use `1..100`.

---

# Public versus Internal Models

Public API models are defined in:

```text
src/schemas.py
```

`src/simulation/schemas.py` currently contains `SimulationRunResponse`, but no endpoint uses it in `v0.11.1`. It is preparation for a later public simulation API and must not be interpreted as an already exposed REST resource.
