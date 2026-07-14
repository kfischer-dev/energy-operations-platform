# Data Dictionary

## Purpose

This document is the authoritative domain and field reference for the Energy Operations Platform data model in `v0.10.0`.

The model is intentionally realistic enough to support later simulation, weather influence, energy balance and dashboard work without becoming a full electrical-grid model.

## Core Domain Model

```text
regions
   └── assets ── asset_types
          ├── measurements
          └── storage_specs
```

## General Conventions

- Internal active power uses `kW`.
- Interval energy uses `kWh`.
- Timestamps use PostgreSQL `TIMESTAMPTZ`.
- Technical codes are stable identifiers; display names may change.
- Development regions are schematic model regions, not postal-code areas or official control zones.
- Valid-only KPI calculations include only `quality_status = 'valid'`.
- `invalid` and `estimated` rows remain stored but are excluded from current KPI endpoints.

---

# Entity: Region

Regions group assets for later regional analytics, weather generation, energy balance and map visualization.

Initial development regions:

```text
DE-NORTH
DE-SOUTH
DE-EAST
DE-WEST
```

| Field | PostgreSQL type | Required | Rules | Description |
|---|---|---:|---|---|
| `region_id` | `INT IDENTITY` | yes | primary key | Internal database identifier |
| `region_code` | `VARCHAR(15)` | yes | unique | Stable technical code, for example `DE-SOUTH` |
| `region_prefix` | `VARCHAR(5)` | yes | unique | Short prefix used in asset codes, for example `S` |
| `region_name` | `VARCHAR(255)` | yes | unique | Human-readable region name |
| `region_description` | `TEXT` | no | – | Optional model-region description |
| `created_at` | `TIMESTAMPTZ` | yes | defaults to current timestamp | Record creation time |

### Meaning of `region_code`

`region_code` is not a postcode. It is a stable internal identifier for APIs, filters, seed data and frontend logic.

---

# Entity: Asset Type

`asset_types` stores reusable technical classifications. It prevents classification attributes from being repeated for every asset.

| Field | PostgreSQL type | Required | Rules | Description |
|---|---|---:|---|---|
| `asset_type_id` | `INT IDENTITY` | yes | primary key | Internal type identifier |
| `asset_type_name` | `VARCHAR(100)` | yes | unique | Stable type name such as `wind_park` |
| `asset_prefix` | `VARCHAR(10)` | yes | unique | Code component such as `WIND` or `BESS` |
| `asset_role` | `VARCHAR(30)` | yes | checked enum | Main role of the asset type |
| `is_renewable` | `BOOLEAN` | yes | – | Whether the technology is classified as renewable |
| `is_weather_dependent` | `BOOLEAN` | yes | – | Whether later output simulation depends strongly on weather |
| `is_dispatchable` | `BOOLEAN` | yes | – | Whether output or operation can be controlled within the simplified model |
| `can_store_energy` | `BOOLEAN` | yes | – | Whether the type represents energy storage |
| `created_at` | `TIMESTAMPTZ` | yes | defaults to current timestamp | Record creation time |

## Allowed Asset Roles

```text
producer
consumer
storage
grid
```

### Role meanings

| Role | Meaning |
|---|---|
| `producer` | Generates electrical energy |
| `consumer` | Consumes electrical energy |
| `storage` | Charges, stores and later discharges energy |
| `grid` | Represents simplified grid infrastructure or power transfer |

## Current Development Asset Types

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

### Grid infrastructure

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

### `is_dispatchable`

Within this project, dispatchable means that the asset's output or operation can be intentionally adjusted in the later simplified simulation. It does not claim to reproduce all real operational, market or grid constraints.

---

# Entity: Asset

An asset is a physical or modeled energy-system object assigned to one region and one reusable asset type.

| Field | PostgreSQL type | Unit | Required | Rules | Description |
|---|---|---:|---:|---|---|
| `asset_id` | `INT IDENTITY` | – | yes | primary key | Internal identifier |
| `asset_code` | `VARCHAR(50)` | – | yes | unique | Stable technical code, for example `S-BESS-001` |
| `asset_name` | `VARCHAR(255)` | – | yes | – | Human-readable name |
| `asset_location` | `VARCHAR(255)` | – | yes | – | Human-readable location label |
| `rated_power_kw` | `NUMERIC(12,2)` | kW | yes | `> 0` | Rated or representative maximum power |
| `operating_status` | `VARCHAR(20)` | – | yes | checked enum | Current operational master-data status |
| `latitude` | `NUMERIC(9,6)` | degrees | yes | `-90` to `90` | Map latitude |
| `longitude` | `NUMERIC(9,6)` | degrees | yes | `-180` to `180` | Map longitude |
| `asset_type_id` | `INT` | – | yes | FK to `asset_types` | Technical classification |
| `region_id` | `INT` | – | yes | FK to `regions` | Regional assignment |
| `created_at` | `TIMESTAMPTZ` | – | yes | defaults to current timestamp | Record creation time |

## Operating Status Values

```text
online
offline
maintenance
fault
```

`operating_status` currently represents the latest master-data state. Historical status changes are not yet stored as events.

## Rated Power Interpretation

The field is intentionally generic across asset roles:

| Role | Interpretation |
|---|---|
| Producer | Installed or rated generation power |
| Consumer | Representative peak or configured demand capacity |
| Storage | Simplified rated power; detailed charge/discharge limits are stored in `storage_specs` |
| Grid | Simplified transfer or equipment rating |

---

# Entity: Measurement

Measurements store interval-based time-series values for one asset.

| Field | PostgreSQL type | Unit | Required | Rules | Description |
|---|---|---:|---:|---|---|
| `measurement_id` | `INT IDENTITY` | – | yes | primary key | Internal measurement identifier |
| `asset_id` | `INT` | – | yes | FK to `assets`, cascade delete | Parent asset |
| `measurement_time` | `TIMESTAMPTZ` | – | yes | unique together with `asset_id` | Interval reference timestamp |
| `interval_minutes` | `INT` | minutes | yes | `> 0` | Duration represented by the row |
| `active_power_kw` | `NUMERIC(20,2)` | kW | yes | signed values allowed | Average active power during the interval |
| `energy_kwh` | `NUMERIC(20,2)` | kWh | yes | `>= 0` | Interval energy magnitude |
| `source` | `VARCHAR(255)` | – | yes | – | Data origin such as `simulation`, `pytest`, `import` or `manual` |
| `quality_status` | `VARCHAR(20)` | – | yes | checked enum | Data-quality classification |
| `created_at` | `TIMESTAMPTZ` | – | yes | defaults to current timestamp | Record creation time |

## Uniqueness Rule

```text
UNIQUE (asset_id, measurement_time)
```

One asset cannot have two measurement records at the same timestamp.

## Power and Energy

For a regular interval, the expected relationship is:

```text
energy_kwh = ABS(active_power_kw) × interval_minutes / 60
```

The database currently does not enforce this formula. The separation is intentional:

- power describes the interval's rate or level,
- energy describes the quantity over the interval,
- future imports may contain calculated or metered energy,
- analytics can aggregate `energy_kwh` directly.

## Signed Active Power

The database permits signed `active_power_kw` values.

Current use:

- normal development seed values are positive,
- deterministic test data contains negative rows marked `invalid`,
- future storage or grid-flow conventions may use direction explicitly.

No final platform-wide sign convention for charging, discharging, import and export has been implemented yet. A later simulation version should add an explicit operating mode or documented direction convention before signed values are used as valid operational data.

## Quality Status Values

```text
valid
invalid
estimated
```

| Status | Meaning | Included in current KPIs |
|---|---|---:|
| `valid` | Accepted operational value | yes |
| `invalid` | Known bad or rejected value | no |
| `estimated` | Derived or substituted value | no |

---

# Entity: Storage Specs

`storage_specs` is a one-to-one extension of `assets` for static battery-storage specifications.

| Field | PostgreSQL type | Unit | Required | Rules | Description |
|---|---|---:|---:|---|---|
| `asset_id` | `INT` | – | yes | PK and FK to `assets`, cascade delete | Storage asset identifier |
| `energy_capacity_kwh` | `NUMERIC(20,2)` | kWh | yes | `> 0` | Usable or modeled energy capacity |
| `max_charge_power_kw` | `NUMERIC(20,2)` | kW | yes | `> 0` | Maximum charging power |
| `max_discharge_power_kw` | `NUMERIC(20,2)` | kW | yes | `> 0` | Maximum discharging power |
| `charge_efficiency_percent` | `NUMERIC(5,2)` | % | yes | `> 0` and `<= 100` | Charging efficiency |
| `discharge_efficiency_percent` | `NUMERIC(5,2)` | % | yes | `> 0` and `<= 100` | Discharging efficiency |
| `min_state_of_charge_percent` | `NUMERIC(5,2)` | % | yes | `0` to `100` | Lower operating limit |
| `max_state_of_charge_percent` | `NUMERIC(5,2)` | % | yes | `0` to `100` and greater than minimum | Upper operating limit |
| `created_at` | `TIMESTAMPTZ` | – | yes | defaults to current timestamp | Record creation time |

Dynamic state of charge is not part of this static table. It will later be modeled as time-dependent simulation or measurement data.

---

# API Naming versus Database Naming

The database uses:

```text
asset_types.asset_type_name
```

The public API exposes the joined value as:

```text
asset_type
```

This keeps the external contract concise while preserving a descriptive internal database column name.

---

# Derived KPI Fields

The following API fields are calculated from valid measurements and are not stored as columns:

| Field | Calculation |
|---|---|
| `measurement_count` | `COUNT(*)` |
| `average_power_kw` | rounded `AVG(active_power_kw)` |
| `min_power_kw` | `MIN(active_power_kw)` |
| `max_power_kw` | `MAX(active_power_kw)` |
| `total_energy_kwh` | `SUM(energy_kwh)` |
| `latest_measurement_time` | `MAX(measurement_time)` |

---

# Planned Later Entities and Fields

## Simulation Runs

Likely fields:

```text
simulation_run_id
simulation_mode
start_time
end_time
interval_minutes
simulation_speed
run_status
created_at
```

## Weather Measurements

Likely fields:

```text
region_id
weather_time
cloud_cover_percent
solar_irradiance_w_m2
wind_speed_m_s
temperature_c
source
```

## Dynamic Storage State

Likely fields:

```text
asset_id
measurement_time
state_of_charge_percent
storage_mode
charge_or_discharge_power_kw
```

## Energy Balance

Likely calculated outputs:

```text
total_generation_kw
total_consumption_kw
storage_contribution_kw
grid_flow_kw
surplus_kw
deficit_kw
balance_status
```

## Recommendations

Likely actions:

```text
charge_storage
discharge_storage
activate_dispatchable_generation
reduce_consumption
no_action
```

---

# Explicitly Out of Scope for the Current MVP

- voltage and current time series,
- reactive power and power factor,
- physically accurate grid-frequency simulation,
- transmission lines and full grid topology,
- AC power-flow calculations,
- detailed equipment condition monitoring,
- predictive maintenance,
- market bidding and pricing,
- authentication and authorization.

The current model is a backend and analytics foundation, not a certified power-system simulator.
