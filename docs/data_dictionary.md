# Data Dictionary

## Purpose

This document defines the planned domain data model for the Energy Operations Platform from `v0.10.0` onward.

The goal is to support a realistic but intentionally simplified energy backend with:

- regions,
- producers, consumers and storage assets,
- time-series measurements,
- later simulation, weather, energy balance and recommendations,
- future visualization in a React dashboard.

The model should remain small enough for the portfolio MVP while avoiding later structural changes that are already foreseeable.

---

## Core Modeling Decisions

- The existing `assets` concept will be replaced by the broader `assets` concept.
- `asset_type` will become `asset_type`.
- API routes should move from `/assets` to `/assets` during the `v0.10.x` block.
- Internal power values will use `kW`.
- `load_value` will become `active_power_kw`.
- Measurements will include both power and interval energy.
- Storage-specific master data will be stored separately in `storage_specs`.
- Weather will be introduced in a later dedicated version.
- Grid frequency will not be simulated in the first MVP because a physically meaningful model would require substantially more grid dynamics.

---

## Data Categories

### Master Data

Values that change rarely:

- region
- asset name
- asset role
- asset type
- rated power
- coordinates
- operating status
- storage specifications

### Time-Series Data

Values generated or measured over time:

- measurement timestamp
- active power
- interval energy
- data quality
- later state of charge and weather values

### Context and Influence Data

Values that later influence generation or consumption:

- cloud cover
- solar irradiance
- wind speed
- temperature
- weekday
- time of day

### Derived Data

Values calculated from stored or simulated data:

- regional generation
- regional consumption
- surplus
- deficit
- energy balance
- recommendations
- later simplified system-state indicators

---

# Entity: Region

Regions are schematic aggregation areas used for filters, analytics, weather simulation, energy balance and later map visualization.

Initial examples:

- `DE-NORTH`
- `DE-SOUTH`
- `DE-EAST`
- `DE-WEST`

| Field | Type | Required | Description | MVP Priority |
|---|---|---:|---|---|
| `region_id` | integer | yes | Primary key | must |
| `region_code` | text | yes | Stable technical code, for example `DE-NORTH` | must |
| `region_name` | text | yes | Human-readable display name | must |

### Notes

`region_code` is not a postal code. It is a stable technical identifier for APIs, seed data, filters and frontend logic.

Optional future fields:

- `country_code`
- `description`

---

# Entity: Asset

The existing `assets` table will be replaced by `assets`.

An asset can represent:

- an energy producer,
- a consumer,
- or a storage system.

| Field | Type | Unit | Required | Description | MVP Priority |
|---|---|---:|---:|---|---|
| `asset_id` | integer | – | yes | Primary key | must |
| `asset_name` | text | – | yes | Human-readable asset name | must |
| `asset_role` | text | – | yes | `producer`, `consumer` or `storage` | must |
| `asset_type` | text | – | yes | Concrete asset type | must |
| `region_id` | integer | – | yes | Foreign key to `regions` | must |
| `rated_power_kw` | numeric | kW | yes | Rated or maximum relevant power | must |
| `latitude` | numeric | degrees | yes | Map position | should |
| `longitude` | numeric | degrees | yes | Map position | should |
| `operating_status` | text | – | yes | Current status such as `online`, `offline`, `maintenance`, `fault` | should |

## Allowed Asset Roles and Types

| Asset Role | Allowed Asset Types |
|---|---|
| `producer` | `solar_park`, `wind_park`, `hydro_plant`, `reserve_plant` |
| `consumer` | `city`, `industrial_site`, `charging_park` |
| `storage` | `battery_storage` |

### Rated Power Interpretation

- Producer: installed generation capacity
- Consumer: maximum or representative demand capacity
- Storage: simplified rated charge/discharge power

Storage energy capacity is modeled separately in `storage_specs`.

---

# Entity: Measurement

Measurements represent time-series power and interval energy values for an asset.

| Field | Type | Unit | Required | Description | MVP Priority |
|---|---|---:|---:|---|---|
| `measurement_id` | integer | – | yes | Primary key | must |
| `asset_id` | integer | – | yes | Foreign key to `assets` | must |
| `measurement_time` | timestamp | – | yes | Start or reference time of the interval | must |
| `interval_minutes` | integer | minutes | yes | Measurement interval duration | must |
| `active_power_kw` | numeric | kW | yes | Average active power during the interval | must |
| `energy_kwh` | numeric | kWh | yes | Energy generated, consumed or transferred during the interval | must |
| `source` | text | – | yes | Example: `simulation`, `scada`, `manual`, `import` | must |
| `quality_status` | text | – | yes | `valid`, `invalid` or `estimated` | must |

## Power and Energy

`active_power_kw` describes power.

`energy_kwh` describes energy over the measurement interval.

For regular intervals:

```text
energy_kwh = active_power_kw × interval_minutes / 60
```

Both values will be stored because:

- the API can expose them directly,
- later analytics can aggregate energy efficiently,
- irregular intervals remain possible,
- the distinction is important for realistic energy-domain behavior.

## Role Interpretation

- Producer: power and energy generated
- Consumer: power and energy consumed
- Storage: power and energy charged or discharged

Storage direction will later be made explicit through a storage operating mode.

---

# Entity: Storage Specs

Storage-specific master data belongs in a separate table because it does not apply to producers or consumers.

| Field | Type | Unit | Required | Description | MVP Priority |
|---|---|---:|---:|---|---|
| `asset_id` | integer | – | yes | Primary key and foreign key to `assets` | must |
| `energy_capacity_kwh` | numeric | kWh | yes | Usable storage energy capacity | must |
| `max_charge_power_kw` | numeric | kW | yes | Maximum charging power | must |
| `max_discharge_power_kw` | numeric | kW | yes | Maximum discharging power | must |
| `charge_efficiency_percent` | numeric | % | yes | Charging efficiency | should |
| `discharge_efficiency_percent` | numeric | % | yes | Discharging efficiency | should |
| `min_state_of_charge_percent` | numeric | % | yes | Lower operating limit | should |
| `max_state_of_charge_percent` | numeric | % | yes | Upper operating limit | should |

Dynamic values such as `state_of_charge_percent` and `operating_mode` will be introduced later as time-dependent data.

---

# Planned Later Entities

## Weather Measurements

Planned for a dedicated weather version.

Likely fields:

- `region_id`
- `weather_time`
- `cloud_cover_percent`
- `solar_irradiance_w_m2`
- `wind_speed_m_s`
- `temperature_c`
- `source`

## Simulation Runs

Planned for the simulation foundation.

Likely fields:

- simulation mode
- start time
- end time
- interval length
- simulation speed
- run status

## Energy Balance

Initially may be calculated dynamically rather than stored.

Likely outputs:

- total generation
- total consumption
- storage contribution
- regional balance
- surplus
- deficit

## Recommendations

Planned after the balance logic exists.

Likely actions:

- `charge_storage`
- `discharge_storage`
- `activate_reserve`
- `reduce_consumption`
- `no_action`

---

# Explicitly Out of Scope for the First MVP

The following fields are realistic in operational energy systems but are intentionally excluded for now:

- voltage
- current
- reactive power
- power factor
- detailed frequency simulation
- grid topology
- transformers and transmission lines
- condition-monitoring data such as vibration and bearing temperature
- turbine-specific or charger-specific detail tables
- predictive-maintenance data
- physically accurate power-flow calculations

## Frequency Decision

Grid frequency is operationally important, but a meaningful frequency simulation requires grid dynamics, inertia and control behavior.

For the first MVP, the platform will use energy-balance states such as:

- `balanced`
- `surplus`
- `deficit`
- `critical_deficit`

A later simplified field such as `estimated_frequency_hz` may be added only if it is clearly documented as an educational approximation.

---

# v0.10.0 Implementation Scope

The first implementation step should include:

## New Table

- `regions`

## Renamed and Extended Table

- `assets` → `assets`
- `asset_id` → `asset_id`
- `asset_name` → `asset_name`
- `asset_type` → `asset_type`
- `asset_location` may be removed or replaced by region and coordinates

New fields:

- `asset_role`
- `region_id`
- `rated_power_kw`
- `latitude`
- `longitude`
- `operating_status`

## Updated Measurements

- `asset_id` → `asset_id`
- `load_value` → `active_power_kw`
- remove variable-unit handling and use `kW` internally
- add `interval_minutes`
- add `energy_kwh`

## New Storage Table

- `storage_specs`

Weather, simulation runs, balance and recommendations remain planned but are not implemented in `v0.10.0`.
