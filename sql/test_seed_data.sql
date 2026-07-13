-- ============================================================
-- Test Seed Data
-- Energy Operations Platform
-- ============================================================
-- Purpose:
-- Provides deterministic test data for automated API tests.
--
-- Important:
-- Run this ONLY against the test database, not against the
-- development or production database.
-- ============================================================


-- ============================================================
-- Reset tables
-- ============================================================

TRUNCATE TABLE measurements, assets RESTART IDENTITY CASCADE;


-- ============================================================
-- Insert test assets
-- ============================================================

INSERT INTO assets (asset_name, asset_type, asset_location)
VALUES
    ('Asset A', 'solar_park', 'Stuttgart'),
    ('Asset B', 'wind_park', 'Ulm'),
    ('Asset C', 'hydro_power', 'Heidelberg'),
    ('Asset D', 'battery_storage', 'Karlsruhe'),
    ('Asset E', 'substation', 'Waiblingen'),
    ('Asset F', 'solar_park', 'Freiburg'),
    ('Asset G', 'wind_park', 'Mannheim'),
    ('Asset H', 'grid_connection', 'Heilbronn'),
    ('Asset Z', 'solar_park', 'Berlin');


-- ============================================================
-- Insert test measurements
-- ============================================================
-- Notes:
-- Asset Z intentionally has no measurements.
-- Asset D contains invalid negative values for quality filtering tests.
-- KPI endpoints should usually evaluate only quality_status = 'valid'.
-- ============================================================

INSERT INTO measurements (
    asset_id,
    measurement_time,
    load_value,
    unit,
    source,
    quality_status
)
VALUES
    -- Asset A: 3 valid measurements
    (1, '2026-06-22 08:15:00', 80.50, 'kW', 'CSV Import', 'valid'),
    (1, '2026-06-22 08:30:00', 95.25, 'kW', 'CSV Import', 'valid'),
    (1, '2026-06-22 08:45:00', 101.75, 'kW', 'CSV Import', 'valid'),

    -- Asset B: 3 valid measurements
    (2, '2026-06-22 08:15:00', 120.75, 'kW', 'CSV Import', 'valid'),
    (2, '2026-06-22 08:30:00', 135.20, 'kW', 'CSV Import', 'valid'),
    (2, '2026-06-22 08:45:00', 128.40, 'kW', 'CSV Import', 'valid'),

    -- Asset C: 3 valid measurements
    (3, '2026-06-22 08:15:00', 210.00, 'kW', 'CSV Import', 'valid'),
    (3, '2026-06-22 08:30:00', 205.50, 'kW', 'CSV Import', 'valid'),
    (3, '2026-06-22 08:45:00', 198.75, 'kW', 'CSV Import', 'valid'),

    -- Asset D: invalid negative values + one valid value
    (4, '2026-06-22 08:15:00', -45.00, 'kW', 'CSV Import', 'invalid'),
    (4, '2026-06-22 08:30:00', -38.50, 'kW', 'CSV Import', 'invalid'),
    (4, '2026-06-22 08:45:00', 25.00, 'kW', 'CSV Import', 'valid'),

    -- Asset E: high-load valid measurements
    (5, '2026-06-22 08:15:00', 450.80, 'kW', 'Sensor API', 'valid'),
    (5, '2026-06-22 08:30:00', 480.30, 'kW', 'Sensor API', 'valid'),
    (5, '2026-06-22 08:45:00', 510.90, 'kW', 'Sensor API', 'valid'),

    -- Asset F: solar park with moderate values
    (6, '2026-06-22 08:15:00', 60.25, 'kW', 'CSV Import', 'valid'),
    (6, '2026-06-22 08:30:00', 72.40, 'kW', 'CSV Import', 'valid'),
    (6, '2026-06-22 08:45:00', 88.10, 'kW', 'CSV Import', 'valid'),

    -- Asset G: wind park with sensor data
    (7, '2026-06-22 08:15:00', 155.00, 'kW', 'Sensor API', 'valid'),
    (7, '2026-06-22 08:30:00', 162.75, 'kW', 'Sensor API', 'valid'),
    (7, '2026-06-22 08:45:00', 149.30, 'kW', 'Sensor API', 'valid'),

    -- Asset H: grid connection with high SCADA values
    (8, '2026-06-22 08:15:00', 720.00, 'kW', 'SCADA', 'valid'),
    (8, '2026-06-22 08:30:00', 760.50, 'kW', 'SCADA', 'valid'),
    (8, '2026-06-22 08:45:00', 790.25, 'kW', 'SCADA', 'valid');