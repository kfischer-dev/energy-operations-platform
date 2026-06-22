-- =============================================================
-- Database schema for the Energy Operations Platform

-- Table: stations
-- Stores technical assets such as transformer stations, solar parks or wind parks.

-- Table: measurements
-- Stores measured values that belong to a station.

-- Relationship:
-- One station can have many measurements.
-- Each measurement belongs to exactly one station.
-- measurements.station_id references stations.id
-- =============================================================

CREATE TABLE stations (
    station_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    station_type VARCHAR(100) NOT NULL,
    location VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE measurements (
    measurement_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    station_id INT NOT NULL,
    measurement_time TIMESTAMP NOT NULL,
    load_value NUMERIC(10, 2) NOT NULL,
    unit VARCHAR(10) NOT NULL,
    source VARCHAR(255) NOT NULL,
    quality_status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (station_id) REFERENCES stations(station_id)
);
