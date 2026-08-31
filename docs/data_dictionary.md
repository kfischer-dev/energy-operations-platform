# Data Dictionary

## Purpose

This document is the authoritative field and domain reference for the Energy Operations Platform in `v0.11.0`.

It covers:

- PostgreSQL tables,
- public API models,
- internal measurement/aggregation models,
- internal simulation models,
- the temporary measurement compatibility state introduced by `v0.11.0`.

---

# Core Domain

## Regions

Regions are schematic model areas used to group assets. They are not official TSO control areas.

| Field | Type | Meaning |
|---|---|---|
| `region_id` | integer | Surrogate primary key |
| `region_code` | string | Stable technical code such as `DE-NORTH` |
| `region_prefix` | string | Short prefix used in asset codes |
| `region_name` | string | Human-readable name |
| `region_description` | text, nullable | Additional description |
| `created_at` | timestamp with time zone | Creation timestamp |

Development seed regions:

```text
DE-NORTH
DE-SOUTH
DE-EAST
DE-WEST
```

---

# Asset Types

`asset_types` normalizes reusable technical categories and capability flags.

| Field | Type | Meaning |
|---|---|---|
| `asset_type_id` | integer | Surrogate primary key |
| `asset_type_name` | string | Stable type name |
| `asset_prefix` | string | Short code component |
| `asset_role` | enum-like string | `producer`, `consumer`, `storage`, `grid` |
| `is_renewable` | boolean | Renewable generation flag |
| `is_weather_dependent` | boolean | Whether external conditions influence operation |
| `is_dispatchable` | boolean | Whether output/load can be deliberately controlled |
| `can_store_energy` | boolean | Whether the type stores energy |
| `created_at` | timestamp with time zone | Creation timestamp |

Development seed types:

### Producers

```text
solar_park
wind_park
hydro_power_plant
gas_power_plant
biomass_power_plant
```

### Storage

```text
battery_storage
```

### Grid

```text
substation
```

### Consumers

```text
residential_load
commercial_load
industrial_load
city_load
ev_charging_park
data_center
```

Only four producer types are registered for runtime simulation in `v0.11.0`:

```text
solar_park
wind_park
hydro_power_plant
biomass_power_plant
```

---

# Assets

`assets` stores physical/technical energy-system master data.

| Field | Type | Rules / meaning |
|---|---|---|
| `asset_id` | integer | Identity primary key |
| `asset_code` | string | Unique stable technical code |
| `asset_name` | string | Human-readable name |
| `asset_location` | string | Location description |
| `rated_power_kw` | numeric | Must be `> 0` |
| `operating_status` | string | `online`, `offline`, `maintenance`, `fault` |
| `latitude` | numeric | `-90..90` |
| `longitude` | numeric | `-180..180` |
| `asset_type_id` | integer | FK to `asset_types` |
| `region_id` | integer | FK to `regions` |
| `created_at` | timestamp with time zone | Creation timestamp |

`rated_power_kw` represents the technical upper power reference used by the simulation engine. Generated producer power is validated against it.

---

# Simulation Runs

`simulation_runs` stores metadata and lifecycle state for a persisted simulation execution.

| Field | Type | Rules / meaning |
|---|---|---|
| `simulation_run_id` | bigint | Identity primary key |
| `simulation_mode` | string | `historical`, `live`, `forecast`, `scenario` |
| `start_time` | timestamp with time zone | Configured start |
| `end_time` | timestamp with time zone | Configured end; must be after start |
| `interval_minutes` | integer | Positive configured grid interval |
| `random_seed` | integer, nullable | Non-negative deterministic seed |
| `status` | string | `created`, `running`, `completed`, `failed` |
| `generated_measurement_count` | integer | Number of point-in-time measurements persisted by the run |
| `created_at` | timestamp with time zone | Run metadata creation time |
| `started_at` | timestamp with time zone, nullable | Set when marked running |
| `completed_at` | timestamp with time zone, nullable | Set on completed or failed |

### Run status lifecycle

Successful path:

```text
created → running → completed
```

Failure path:

```text
created → running → failed
```

`generated_measurement_count` counts persisted **PowerMeasurement rows**, not derived `PowerIntervalDraft` objects.

Example for four assets over two hours at 15-minute resolution:

```text
8 complete intervals per asset
9 grid points per asset
4 × 9 = 36 persisted measurements
4 × 8 = 32 derived intervals
```

---

# Measurements

## Current PostgreSQL fields

| Field | Type | Rules / meaning |
|---|---|---|
| `measurement_id` | integer | Identity primary key |
| `asset_id` | integer | Required FK to `assets`, `ON DELETE CASCADE` |
| `simulation_run_id` | bigint, nullable | FK to `simulation_runs`, `ON DELETE SET NULL` |
| `measurement_time` | timestamp with time zone | Point-in-time timestamp represented by the row |
| `active_power_kw` | numeric | Required active-power value |
| `source` | string | Origin of the row |
| `quality_status` | string | `valid`, `invalid`, `estimated` |
| `created_at` | timestamp with time zone | Creation timestamp |

Uniqueness:

```text
(asset_id, measurement_time)
```

## Point-in-time semantics

A measurement row answers:

> What was the active power of this asset at this timestamp?

Raw measurements deliberately do **not** store:

```text
interval_minutes
energy_kwh
```

Energy and interval-average power are derived from a sequence of raw power measurements. This keeps the raw model independent of later analysis interval choices.

`simulation_run_id` is nullable because measurements may originate from simulation or from other sources. `simulation_runs.interval_minutes` remains part of the simulation configuration.

# Storage Specifications

`storage_specs` stores static battery characteristics in a one-to-one relationship with an asset.

| Field | Type | Meaning / constraint |
|---|---|---|
| `asset_id` | integer | PK and FK to `assets` |
| `energy_capacity_kwh` | numeric | Must be `> 0` |
| `max_charge_power_kw` | numeric | Must be `> 0` |
| `max_discharge_power_kw` | numeric | Must be `> 0` |
| `charge_efficiency_percent` | numeric | `> 0` and `<= 100` |
| `discharge_efficiency_percent` | numeric | `> 0` and `<= 100` |
| `min_state_of_charge_percent` | numeric | `0..100` |
| `max_state_of_charge_percent` | numeric | `0..100` and greater than minimum |
| `created_at` | timestamp with time zone | Creation timestamp |

Dynamic state of charge is not yet persisted or simulated in `v0.11.0`.

---

# Public API Models

## `AssetSummaryResponse`

```text
asset_id
asset_name
asset_code
asset_location
asset_role
asset_type
region_code
rated_power_kw
operating_status
```

## `AssetResponse`

Adds:

```text
region_id
region_name
latitude
longitude
```

## `MeasurementSummaryResponse`

```text
measurement_id
asset_id
asset_code
asset_name
measurement_time
active_power_kw
quality_status
```

## `MeasurementResponse`

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

`simulation_run_id` remains an internal database relationship and is not currently exposed in this response.

## `MeasurementCreate`

```text
asset_id
measurement_time
active_power_kw
source
quality_status
```

POST-created and simulation-created rows therefore share the same canonical raw measurement model.

## KPI response models

Global and asset KPI responses are period based.

Common fields:

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

Asset-specific responses additionally expose asset identity fields.

Measured fields:

```text
measurement_count
min_measured_power_kw
max_measured_power_kw
```

Derived fields:

```text
avg_active_power_kw
total_energy_kwh
coverage_ratio
```

Boundary supports can contribute to derived fields without changing measured count/min/max.

# Internal Measurement Models

Defined in `src/measurements/models.py`.

## `PowerMeasurement`

One raw point-in-time active-power value.

| Field | Meaning |
|---|---|
| `asset_id` | Owning asset |
| `measurement_time` | Point timestamp |
| `active_power_kw` | Active power at the point |
| `source` | Measurement source |
| `quality_status` | `valid`, `invalid`, `estimated` |

Supported internal source literals:

```text
simulation
database
scada
smart_meter
csv_import
external_api
```

Runtime simulation currently uses `source = "simulation"` and `quality_status = "valid"`.

## `PowerSupportPoint`

Temporary aggregation point.

```text
timestamp
active_power_kw
point_type
is_interpolated
```

Support-point types:

```text
measured
interpolated
estimated
```

Interpolated support points are derived values and are never persisted as source measurements.

## `PowerSegment`

Represents one adjacent pair of support points:

```text
start_point
end_point
```

Energy for the segment is calculated with the trapezoidal rule.

## `PowerIntervalDraft`

Derived interval result; it is currently returned in memory and not persisted.

| Field | Meaning |
|---|---|
| `asset_id` | Owning asset |
| `interval_start` | Interval start |
| `interval_end` | Interval end |
| `avg_active_power_kw` | Time-weighted average power, nullable if no coverage |
| `energy_kwh` | Derived energy, nullable if no segments can be built |
| `quality_status` | `valid`, `incomplete`, `estimated`, `invalid` type contract |
| `aggregation_method` | Current value: `linear_interpolation_trapezoidal` |
| `source_measurement_count` | Raw measurements relevant to this exact interval |
| `valid_measurement_count` | Relevant measurements remaining after invalid raw rows are excluded |
| `coverage_ratio` | Covered duration divided by full interval duration |

Current quality determination is coverage-based:

```text
coverage <= 0.0 → invalid
0.0 < coverage < 1.0 → incomplete
coverage >= 1.0 → valid
```

`estimated` remains available in the interval type contract but is not currently produced by `determine_quality_status()`.

### Source count semantics

`source_measurement_count` does **not** mean the size of the complete input series. It counts only the raw measurements selected as left support, internal measurements and right support for that specific interval.

Example:

```text
Measurements: 10:00, 10:15, 10:30
Interval:     10:00–10:15

source_measurement_count = 2
```

If interval boundaries must be interpolated, the surrounding raw measurements are counted, but the generated interpolated points are not.

---

# Internal Simulation Models

Defined in `src/simulation/models.py`.

## `SimulationConfig`

Immutable run configuration:

```text
start_time
end_time
interval_minutes
random_seed
simulation_mode
```

Validation:

- `start_time < end_time`
- interval in `5`, `15`, `30`, `60`
- mode in `historical`, `live`, `forecast`, `scenario`
- non-negative seed

Derived properties:

```text
duration
duration_minutes
total_intervals
total_grid_points
effective_end_time
effective_duration
```

`total_grid_points = total_intervals + 1`.

## `SimulationAsset`

Internal reduced view of a database asset needed by the engine:

```text
asset_id
asset_code
asset_role
asset_type
region_id
region_code
rated_power_kw
operating_status
is_renewable
is_weather_dependent
is_dispatchable
can_store_energy
```

## `SimulationContext`

Per-timestamp simulation context:

```text
config
current_time
random_generator
solar_factor
wind_factor
load_factor
hydro_factor
biomass_factor
```

The factors are temporary extension points until weather, demand and operating-state models are introduced.

## `SimulationState`

Mutable state container prepared for future stateful simulation:

```text
last_power_kw_by_asset
state_of_charge_percent_by_asset
generated_measurement_count
```

It is not yet the central state mechanism of the `v0.11.0` service flow.

---

# Simulation Profile Registry

`SIMULATION_PROFILE_REGISTRY` maps one asset type to a `SimulationProfileDefinition` containing:

```text
power_profile
default_asset_factory
context_factory
```

Registered in `v0.11.0`:

| Asset type | Default behavior |
|---|---|
| `solar_park` | Triangular daylight profile |
| `wind_park` | Seeded random variation around factor `0.85` |
| `hydro_power_plant` | Stable factor `0.90` |
| `biomass_power_plant` | Stable factor `0.85` |

Only registered asset types are loaded by `load_simulation_assets()`.

---

# `v0.11.1` Contract Result

The point-in-time cleanup planned after `v0.11.0` is now complete:

- raw measurements no longer store interval duration or energy,
- create/read API contracts match the raw database model,
- global and asset KPIs use requested time periods,
- average power, energy and coverage are derived through the aggregation layer,
- global KPI source retrieval selects period data plus the nearest required per-asset supports.

Future schema additions should preserve this distinction between **raw measured values** and **derived analytical results**.

