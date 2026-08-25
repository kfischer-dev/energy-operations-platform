# API Reference

## Purpose

This document describes the public REST API contract of the Energy Operations Platform for `v0.11.0`.

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

## `v0.11.0` Measurement Compatibility Note

`v0.11.0` introduces runtime simulation rows as **point-in-time active-power measurements** while the public measurement API still retains the previous interval-energy contract for manual/API-created data.

Therefore:

- read models allow `interval_minutes = null`,
- read models allow `energy_kwh = null`,
- runtime simulation measurements use both fields as `null`,
- `POST /measurements` still requires both fields,
- the full public contract cleanup is deferred to `v0.11.1`.

There is no public simulation endpoint in `v0.11.0`.

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

Measurement list endpoints intentionally use a compact response. Detail, POST and PATCH endpoints use the complete response contract.

### `MeasurementSummaryResponse`

```text
measurement_id
asset_id
asset_code
asset_name
measurement_time
active_power_kw
energy_kwh           <- nullable in v0.11.0
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
interval_minutes      <- nullable in v0.11.0
active_power_kw
energy_kwh            <- nullable in v0.11.0
source
quality_status
```

Allowed measurement quality values exposed by the API:

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

Example interval-style seed row:

```json
{
  "measurement_id": 1,
  "asset_id": 1,
  "asset_code": "N-WIND-001",
  "asset_name": "North Sea Wind Park",
  "measurement_time": "2026-06-22T08:00:00+02:00",
  "active_power_kw": 80000.0,
  "energy_kwh": 20000.0,
  "quality_status": "valid"
}
```

Runtime simulation summaries use the same shape, but `energy_kwh` is `null` because the service persists point-in-time power values rather than interval energy.

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

Returns one complete measurement using `MeasurementResponse`.

Path parameter:

| Parameter | Type | Rules |
|---|---|---|
| `measurement_id` | integer | `>= 1` |

Example existing interval-style measurement:

```json
{
  "measurement_id": 1,
  "asset_id": 1,
  "asset_code": "N-WIND-001",
  "asset_name": "North Sea Wind Park",
  "asset_type": "wind_park",
  "asset_role": "producer",
  "region_code": "DE-NORTH",
  "measurement_time": "2026-06-22T08:00:00+02:00",
  "interval_minutes": 15,
  "active_power_kw": 80000.0,
  "energy_kwh": 20000.0,
  "source": "simulation",
  "quality_status": "valid"
}
```

For point-in-time simulation measurements created by the `v0.11.0` service, the distinguishing fields are:

```json
{
  "interval_minutes": null,
  "energy_kwh": null,
  "source": "simulation",
  "quality_status": "valid"
}
```

Unknown measurement IDs return `404 Not Found`.

## `POST /measurements`

Creates one measurement for an existing asset.

`v0.11.0` intentionally keeps the previous create contract. Required body:

```json
{
  "asset_id": 1,
  "measurement_time": "2026-07-02T08:15:00+02:00",
  "interval_minutes": 15,
  "active_power_kw": 82000.0,
  "energy_kwh": 20500.0,
  "source": "manual_import",
  "quality_status": "valid"
}
```

Validation rules implemented by `MeasurementCreate`:

- `asset_id >= 1`
- `interval_minutes >= 1`
- `energy_kwh >= 0`
- `source` must not be empty
- `quality_status` must be `valid`, `invalid` or `estimated`

Successful creation returns `201 Created` and the complete `MeasurementResponse`.

Unknown parent assets return `404 Not Found`.

## `PATCH /measurements/{measurement_id}`

Updates only `quality_status`.

Request body:

```json
{
  "quality_status": "estimated"
}
```

Allowed values:

```text
valid
invalid
estimated
```

Successful update returns the complete `MeasurementResponse` with `200 OK`.

Unknown measurements return `404 Not Found`.

---

# KPI Endpoints

## `GET /kpis/measurements`

Returns the global KPI summary using only rows with:

```text
quality_status = valid
```

Response contract:

```text
measurement_count
average_power_kw
min_power_kw
max_power_kw
total_energy_kwh
latest_measurement_time
```

Example:

```json
{
  "measurement_count": 64,
  "average_power_kw": 67481.25,
  "min_power_kw": 5000.0,
  "max_power_kw": 153000.0,
  "total_energy_kwh": 1079700.0,
  "latest_measurement_time": "2026-06-22T08:45:00+02:00"
}
```

## `GET /assets/{asset_id}/kpis`

Returns the same KPI fields scoped to one asset and additionally includes:

```text
asset_id
asset_name
```

Behavior:

- unknown asset → `404 Not Found`
- existing asset without valid measurements → `measurement_count = 0` and nullable KPI fields
- invalid and estimated rows are excluded

## KPI transition note

The current KPI SQL still belongs to the pre-`v0.11` interval-energy model:

```sql
COUNT(*)
AVG(active_power_kw)
MIN(active_power_kw)
MAX(active_power_kw)
SUM(energy_kwh)
MAX(measurement_time)
```

Runtime simulation rows introduced by `v0.11.0` have `energy_kwh = NULL`. The KPI layer is intentionally not fully refactored in this release. `v0.11.1` will align energy calculation and KPI semantics with point-in-time raw measurements and the reusable aggregation module.

---

# Simulation Service in `v0.11.0`

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

`src/simulation/schemas.py` currently contains `SimulationRunResponse`, but no endpoint uses it in `v0.11.0`. It is preparation for a later public simulation API and must not be interpreted as an already exposed REST resource.
