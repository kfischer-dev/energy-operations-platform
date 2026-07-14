# API Reference

## Purpose

This document describes the public REST API contract of the Energy Operations Platform for `v0.10.0`.

Interactive OpenAPI documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## API Base

Default local URL:

```text
http://127.0.0.1:8000
```

All request and response bodies use JSON. Date-time values are returned as ISO 8601 timestamps.

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

The endpoint confirms that FastAPI is running. It does not perform a database query.

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

An unknown `asset_type` returns an empty list.

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

Measurement list endpoints intentionally return compact records. Detail, POST and PATCH endpoints return the complete measurement contract.

### `MeasurementSummaryResponse`

```text
measurement_id
asset_id
asset_code
asset_name
measurement_time
active_power_kw
energy_kwh
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
interval_minutes
active_power_kw
energy_kwh
source
quality_status
```

## `GET /measurements`

Returns measurement summaries across all assets.

Optional query parameter:

| Parameter | Type | Rules |
|---|---|---|
| `limit` | integer | optional, `1` to `100` |

Example response item:

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

## `GET /assets/{asset_id}/measurements`

Returns measurement summaries for one asset.

Parameters:

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

Example response:

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

Unknown measurements return `404 Not Found`.

## `POST /measurements`

Creates a measurement for an existing asset.

Request model: `MeasurementCreate`

```json
{
  "asset_id": 1,
  "measurement_time": "2026-07-14T10:00:00+02:00",
  "interval_minutes": 15,
  "active_power_kw": 82000.0,
  "energy_kwh": 20500.0,
  "source": "simulation",
  "quality_status": "valid"
}
```

Field rules:

| Field | Type | Validation |
|---|---|---|
| `asset_id` | integer | `>= 1` |
| `measurement_time` | datetime | required |
| `interval_minutes` | integer | `>= 1` |
| `active_power_kw` | number | required; database accepts signed values |
| `energy_kwh` | number | `>= 0` |
| `source` | string | at least one character |
| `quality_status` | string | `valid`, `invalid` or `estimated` |

Successful creation returns `201 Created` and the complete `MeasurementResponse`.

Behavior:

1. Validate the request with Pydantic.
2. Check that the parent asset exists.
3. Insert the measurement.
4. Read the created row through the normal detail query.
5. Return the complete API representation.

Important database constraint:

```text
UNIQUE (asset_id, measurement_time)
```

## `PATCH /measurements/{measurement_id}`

Updates only the measurement quality status.

Request model: `MeasurementQualityUpdate`

```json
{
  "quality_status": "invalid"
}
```

Allowed values:

```text
valid
invalid
estimated
```

A successful update returns `200 OK` and the complete updated `MeasurementResponse`.

---

# KPI Endpoints

Only rows with:

```text
quality_status = valid
```

are included. Both `invalid` and `estimated` measurements are excluded.

## `GET /kpis/measurements`

Returns global measurement KPIs.

Response model: `MeasurementKPIsResponse`

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

Fields:

- `measurement_count`
- `average_power_kw`
- `min_power_kw`
- `max_power_kw`
- `total_energy_kwh`
- `latest_measurement_time`

## `GET /assets/{asset_id}/kpis`

Returns valid-only KPIs for one asset.

Response model: `AssetKPIsResponse`

```json
{
  "asset_id": 1,
  "asset_name": "North Sea Wind Park",
  "measurement_count": 4,
  "average_power_kw": 82250.0,
  "min_power_kw": 79000.0,
  "max_power_kw": 86000.0,
  "total_energy_kwh": 82250.0,
  "latest_measurement_time": "2026-06-22T08:45:00+02:00"
}
```

If the asset exists but has no valid measurements:

```json
{
  "asset_id": 9,
  "asset_name": "Example Asset",
  "measurement_count": 0,
  "average_power_kw": null,
  "min_power_kw": null,
  "max_power_kw": null,
  "total_energy_kwh": null,
  "latest_measurement_time": null
}
```

Unknown assets return `404 Not Found`.

---

# Error Behavior

| Scenario | Status |
|---|---:|
| Valid GET, POST or PATCH | `200` or `201` |
| Unknown asset or measurement | `404` |
| Invalid path/query type | `422` |
| ID or limit outside the allowed range | `422` |
| Missing required request field | `422` |
| Unsupported `quality_status` | `422` |
| Empty `source` | `422` |

Central helper functions provide consistent not-found responses:

```text
get_asset_or_404()
get_measurement_or_404()
```

---

# Current API Limitations

- No asset create/update/delete endpoints yet.
- No region or asset-type endpoints yet.
- Asset filtering is currently performed in Python after loading asset summaries.
- List limiting is applied in Python rather than through SQL `LIMIT`.
- POST does not yet validate that `energy_kwh` mathematically matches power and interval.
- Storage state of charge and charge/discharge mode are not yet modeled as time-series fields.
- No pagination, authentication or authorization yet.
- No simulation-control endpoints yet.
