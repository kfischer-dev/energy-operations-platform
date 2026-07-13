-- =============================================================
-- Database schema for the Energy Operations Platform

-- Table: assets
-- Stores technical assets such as transformer assets, solar parks or wind parks.

-- Table: measurements
-- Stores measured values that belong to an asset.

-- Relationship:
-- One asset can have many measurements.
-- Each measurement belongs to exactly one asset.
-- measurements.asset_id references assets.asset_id
-- =============================================================
/*
DROP TABLE IF EXISTS storage_specs;
DROP TABLE IF EXISTS measurements;
DROP TABLE IF EXISTS assets;
DROP TABLE IF EXISTS asset_types;
DROP TABLE IF EXISTS regions;
*/

CREATE TABLE regions(
    region_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    region_code VARCHAR(15) NOT NULL UNIQUE,
    region_name VARCHAR(255) NOT NULL,
    region_description TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE asset_types (
    asset_type_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    asset_type_name VARCHAR(100) NOT NULL UNIQUE,
    asset_type_description TEXT,
    asset_role VARCHAR(30) CHECK (asset_role IN ('producer', 'consumer', 'storage', 'grid_connection')) NOT NULL,

    is_renewable BOOLEAN NOT NULL,
    is_weather_dependent BOOLEAN NOT NULL,
    is_dispatchable BOOLEAN NOT NULL,
    can_store_energy BOOLEAN NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE assets (
    asset_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    asset_code VARCHAR(50) UNIQUE NOT NULL,
    asset_name VARCHAR(255) NOT NULL,
    asset_location VARCHAR(255) NOT NULL,
    rated_power_kw NUMERIC(10, 2) NOT NULL,
    operating_status VARCHAR(20) CHECK (operating_status IN ('online', 'offline', 'maintenance', 'fault')) NOT NULL,
    latitude NUMERIC(9, 6) NOT NULL,
    longitude NUMERIC(9, 6) NOT NULL,

    asset_type_id INT NOT NULL REFERENCES asset_types(asset_type_id),
    region_id INT NOT NULL REFERENCES regions(region_id),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE measurements (
    measurement_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    measurement_time TIMESTAMPTZ NOT NULL,
    interval_minutes INT NOT NULL CHECK (interval_minutes > 0),
    active_power_kw NUMERIC(20, 2) NOT NULL,
    energy_kwh NUMERIC(20, 2) NOT NULL,
    source VARCHAR(255) NOT NULL,
    quality_status VARCHAR(20) CHECK (quality_status IN ('valid', 'invalid', 'estimated')) NOT NULL,

    asset_id INT NOT NULL REFERENCES assets(asset_id),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE storage_specs (
    asset_id INT PRIMARY KEY REFERENCES assets(asset_id),
    energy_capacity_kwh NUMERIC(20, 2) NOT NULL,

    max_charge_power_kw NUMERIC(20, 2) NOT NULL CHECK (max_charge_power_kw > 0),
    max_discharge_power_kw NUMERIC(20, 2) NOT NULL CHECK (max_discharge_power_kw > 0),

    charge_efficiency_percent NUMERIC(5, 2) NOT NULL CHECK (charge_efficiency_percent >= 0 AND charge_efficiency_percent <= 100),
    discharge_efficiency_percent NUMERIC(5, 2) NOT NULL CHECK (discharge_efficiency_percent >= 0 AND discharge_efficiency_percent <= 100),

    min_state_of_charge_percent NUMERIC(5, 2) NOT NULL CHECK (min_state_of_charge_percent >= 0 AND min_state_of_charge_percent <= 100),
    max_state_of_charge_percent NUMERIC(5, 2) NOT NULL CHECK (max_state_of_charge_percent >= 0 AND max_state_of_charge_percent <= 100),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
