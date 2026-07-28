/*
============================================================
 Database schema for the Energy Operations Platform
============================================================

This schema models technical energy assets, their
classifications, regional assignments, measurements
and storage specifications.

Tables:
- regions
  Defines operational regions used for grouping assets.

- asset_types
  Defines reusable asset categories such as producers,
  consumers, storage systems and grid infrastructure.

- assets
  Stores physical energy assets with their location,
  rated power and operational status.

- measurements
  Stores time-series measurement data for each asset,
  including power, energy and data quality information.

- storage_specs
  Stores static technical specifications for battery
  storage assets.

Relationships:
- One region can contain many assets.
- One asset type can be assigned to many assets.
- One asset can have many measurements.
- One storage asset can have exactly one storage
  specification.
- Each measurement belongs to exactly one asset.
- Each storage specification belongs to exactly one asset.

============================================================
*/

/*
DROP TABLE IF EXISTS storage_specs;
DROP TABLE IF EXISTS measurements;
DROP TABLE IF EXISTS simulation_runs;
DROP TABLE IF EXISTS assets;
DROP TABLE IF EXISTS asset_types;
DROP TABLE IF EXISTS regions;
*/


CREATE TABLE regions (
    region_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    region_code VARCHAR(15) NOT NULL UNIQUE,
    region_prefix VARCHAR(5) NOT NULL UNIQUE,
    region_name VARCHAR(255) NOT NULL UNIQUE,
    region_description TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE asset_types (
    asset_type_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    asset_type_name VARCHAR(100) NOT NULL UNIQUE,
    asset_prefix VARCHAR(10) NOT NULL UNIQUE,
    asset_role VARCHAR(30) NOT NULL
        CHECK (asset_role IN ('producer','consumer','storage','grid')),

    is_renewable BOOLEAN NOT NULL,
    is_weather_dependent BOOLEAN NOT NULL,
    is_dispatchable BOOLEAN NOT NULL,
    can_store_energy BOOLEAN NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE assets (
    asset_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    asset_code VARCHAR(50) NOT NULL UNIQUE,
    asset_name VARCHAR(255) NOT NULL,
    asset_location VARCHAR(255) NOT NULL,

    rated_power_kw NUMERIC(12,2) NOT NULL 
        CHECK (rated_power_kw > 0),
    operating_status VARCHAR(20) NOT NULL
        CHECK (operating_status IN ('online','offline','maintenance','fault')),

    latitude NUMERIC(9,6) NOT NULL 
        CHECK (latitude BETWEEN -90 AND 90),
    longitude NUMERIC(9,6) NOT NULL 
        CHECK (longitude BETWEEN -180 AND 180),

    asset_type_id INT NOT NULL REFERENCES asset_types(asset_type_id),
    region_id INT NOT NULL REFERENCES regions(region_id),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE simulation_runs (
    simulation_run_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    simulation_mode VARCHAR(50) NOT NULL,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    interval_minutes INTEGER NOT NULL,
    random_seed INTEGER,
    status VARCHAR(20) NOT NULL,
    generated_measurement_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    CONSTRAINT chk_simulation_runs_time_range
        CHECK (end_time > start_time),

    CONSTRAINT chk_simulation_runs_interval_minutes
        CHECK (interval_minutes > 0),

    CONSTRAINT chk_simulation_runs_random_seed
        CHECK (random_seed >= 0),

    CONSTRAINT chk_simulation_runs_status
        CHECK (status IN ('created', 'running', 'completed', 'failed')),

    CONSTRAINT chk_simulation_runs_measurement_count
        CHECK (generated_measurement_count >= 0)
);


CREATE TABLE measurements (
    measurement_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    asset_id INT NOT NULL REFERENCES assets(asset_id) ON DELETE CASCADE,
    simulation_run_id BIGINT REFERENCES simulation_runs(simulation_run_id) ON DELETE SET NULL,
    measurement_time TIMESTAMPTZ NOT NULL,
    interval_minutes INT NOT NULL 
        CHECK (interval_minutes > 0),

    active_power_kw NUMERIC(20,2) NOT NULL,
    energy_kwh NUMERIC(20,2) NOT NULL 
        CHECK (energy_kwh >= 0),

    source VARCHAR(255) NOT NULL,
    quality_status VARCHAR(20) NOT NULL
        CHECK (quality_status IN ('valid','invalid','estimated')),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_measurements_asset_time UNIQUE (asset_id,measurement_time)
);


CREATE TABLE storage_specs (
    asset_id INT PRIMARY KEY REFERENCES assets(asset_id) ON DELETE CASCADE,
    energy_capacity_kwh NUMERIC(20,2) NOT NULL 
        CHECK (energy_capacity_kwh > 0),

    max_charge_power_kw NUMERIC(20,2) NOT NULL 
        CHECK (max_charge_power_kw > 0),
    max_discharge_power_kw NUMERIC(20,2) NOT NULL 
        CHECK (max_discharge_power_kw > 0),

    charge_efficiency_percent NUMERIC(5,2) NOT NULL
        CHECK (charge_efficiency_percent > 0 AND charge_efficiency_percent <= 100),
    discharge_efficiency_percent NUMERIC(5,2) NOT NULL
        CHECK (discharge_efficiency_percent > 0 AND discharge_efficiency_percent <= 100),

    min_state_of_charge_percent NUMERIC(5,2) NOT NULL
        CHECK (min_state_of_charge_percent >= 0 AND min_state_of_charge_percent <= 100),
    max_state_of_charge_percent NUMERIC(5,2) NOT NULL
        CHECK (max_state_of_charge_percent >= 0 AND max_state_of_charge_percent <= 100),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_storage_soc_range
        CHECK (min_state_of_charge_percent < max_state_of_charge_percent)
);
