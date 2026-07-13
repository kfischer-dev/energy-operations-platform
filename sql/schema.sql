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
DROP TABLE IF EXISTS measurements;
DROP TABLE IF EXISTS assets;
*/

CREATE TABLE assets (
    asset_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    asset_name VARCHAR(255) NOT NULL,
    asset_type VARCHAR(100) NOT NULL,
    asset_location VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE measurements (
    measurement_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    asset_id INT NOT NULL,
    measurement_time TIMESTAMP NOT NULL,
    load_value NUMERIC(10, 2) NOT NULL,
    unit VARCHAR(10) NOT NULL,
    source VARCHAR(255) NOT NULL,
    quality_status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
);

CREATE TABLE regions(
    region_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    region_code VARCHAR(15) NOT NULL UNIQUE,
    region_name VARCHAR(255) NOT NULL,
    region_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
