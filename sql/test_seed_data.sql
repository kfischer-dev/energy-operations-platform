-- ============================================================
-- Test Seed Data
-- Energy Operations Platform
-- ============================================================
-- Purpose:
-- Provides deterministic, realistic test data for automated
-- API, database and KPI tests.
--
-- Important:
-- Run this ONLY against the test database.
-- IDs, timestamps and values are intentionally stable.
-- ============================================================


-- ============================================================
-- Reset tables
-- ============================================================

TRUNCATE TABLE
    storage_specs,
    measurements,
    assets,
    asset_types,
    regions
RESTART IDENTITY CASCADE;


-- ============================================================
-- Insert reference data
-- ============================================================

INSERT INTO regions(region_code,region_prefix,region_name,region_description)
VALUES
    ('DE-NORTH','N','Northern Germany','North Sea, Schleswig-Holstein and Hamburg model region'),
    ('DE-SOUTH','S','Southern Germany','Baden-Württemberg model region'),
    ('DE-EAST','E','Eastern Germany','Berlin and Brandenburg model region'),
    ('DE-WEST','W','Western Germany','Rhine-Ruhr model region');

INSERT INTO asset_types(asset_type_name,asset_prefix,asset_role,is_renewable,is_weather_dependent,is_dispatchable,can_store_energy)
VALUES
    ('solar_park','SOLAR','producer',TRUE,TRUE,FALSE,FALSE),
    ('wind_park','WIND','producer',TRUE,TRUE,FALSE,FALSE),
    ('hydro_power_plant','HYDRO','producer',TRUE,TRUE,TRUE,FALSE),
    ('battery_storage','BESS','storage',FALSE,FALSE,TRUE,TRUE),
    ('city_load','CITY','consumer',FALSE,FALSE,FALSE,FALSE),
    ('industrial_load','IND','consumer',FALSE,FALSE,FALSE,FALSE),
    ('data_center','DC','consumer',FALSE,FALSE,FALSE,FALSE),
    ('substation','SUB','grid',FALSE,FALSE,FALSE,FALSE);


-- ============================================================
-- Insert test assets
-- ============================================================
-- Deterministic IDs after RESTART IDENTITY:
-- 1 to 8 have measurements; asset 9 intentionally has none.
-- ============================================================

INSERT INTO assets(asset_code,asset_name,asset_location,rated_power_kw,operating_status,latitude,longitude,asset_type_id,region_id)
VALUES
    ('N-WIND-001','Test Wind Park North Sea','North Sea',120000.00,'online',54.500000,6.500000,2,1),
    ('N-CITY-001','Test City Load Hamburg','Hamburg',180000.00,'online',53.551086,9.993682,5,1),
    ('S-HYDRO-001','Test Hydro Plant Black Forest','Baden-Württemberg',80000.00,'online',47.999000,8.100000,3,2),
    ('S-BESS-001','Test Battery Storage Stuttgart','Stuttgart',30000.00,'online',48.775846,9.182932,4,2),
    ('S-IND-001','Test Industrial Load Stuttgart','Stuttgart',120000.00,'online',48.760000,9.170000,6,2),
    ('E-SOLAR-001','Test Solar Park Brandenburg','Brandenburg',50000.00,'online',52.400000,13.500000,1,3),
    ('W-DC-001','Test Data Center Rhine-Ruhr','North Rhine-Westphalia',75000.00,'online',51.227741,6.773456,7,4),
    ('W-SUB-001','Test Substation Rhine-Ruhr','North Rhine-Westphalia',250000.00,'online',51.450000,7.010000,8,4),
    ('E-SOLAR-002','Test Asset Without Measurements','Brandenburg',25000.00,'offline',52.520008,13.404954,1,3);

-- ============================================================
-- Insert test measurements
-- ============================================================
-- Notes:
-- - All measurements use 15-minute intervals.
-- - energy_kwh = ABS(active_power_kw) * 0.25.
-- - Asset 5 contains two deliberately invalid negative values.
-- - Asset 7 contains one estimated value.
-- - Asset 9 intentionally has no measurements.
-- - Valid-only KPIs must ignore invalid and estimated rows when
--   the endpoint explicitly filters for quality_status = 'valid'.
-- ============================================================

INSERT INTO measurements(asset_id, measurement_time, interval_minutes, active_power_kw, energy_kwh, source, quality_status)
VALUES
    -- Asset 1: wind generation, fluctuating
    (1,'2026-06-22 08:00:00+02',15,80000.00,20000.00,'simulation','valid'),
    (1,'2026-06-22 08:15:00+02',15,84000.00,21000.00,'simulation','valid'),
    (1,'2026-06-22 08:30:00+02',15,79000.00,19750.00,'simulation','valid'),

    -- Asset 2: city consumption, rising morning load
    (2,'2026-06-22 08:00:00+02',15,138000.00,34500.00,'simulation','valid'),
    (2,'2026-06-22 08:15:00+02',15,143000.00,35750.00,'simulation','valid'),
    (2,'2026-06-22 08:30:00+02',15,149000.00,37250.00,'simulation','valid'),

    -- Asset 3: stable hydro generation
    (3,'2026-06-22 08:00:00+02',15,68000.00,17000.00,'simulation','valid'),
    (3,'2026-06-22 08:15:00+02',15,69000.00,17250.00,'simulation','valid'),
    (3,'2026-06-22 08:30:00+02',15,71000.00,17750.00,'simulation','valid'),

    -- Asset 4: battery discharging into the grid
    (4,'2026-06-22 08:00:00+02',15,15000.00,3750.00,'simulation','valid'),
    (4,'2026-06-22 08:15:00+02',15,12000.00,3000.00,'simulation','valid'),
    (4,'2026-06-22 08:30:00+02',15,8000.00,2000.00,'simulation','valid'),

    -- Asset 5: industrial load with deliberately invalid negatives
    (5,'2026-06-22 08:00:00+02',15,-92000.00,23000.00,'simulation','invalid'),
    (5,'2026-06-22 08:15:00+02',15,-97000.00,24250.00,'simulation','invalid'),
    (5,'2026-06-22 08:30:00+02',15,102000.00,25500.00,'simulation','valid'),

    -- Asset 6: solar generation, increasing after sunrise
    (6,'2026-06-22 08:00:00+02',15,18000.00,4500.00,'simulation','valid'),
    (6,'2026-06-22 08:15:00+02',15,22500.00,5625.00,'simulation','valid'),
    (6,'2026-06-22 08:30:00+02',15,27000.00,6750.00,'simulation','valid'),

    -- Asset 7: stable data-center load, one estimated value
    (7,'2026-06-22 08:00:00+02',15,62000.00,15500.00,'simulation','valid'),
    (7,'2026-06-22 08:15:00+02',15,62500.00,15625.00,'simulation','estimated'),
    (7,'2026-06-22 08:30:00+02',15,63000.00,15750.00,'simulation','valid'),

    -- Asset 8: substation power flow
    (8,'2026-06-22 08:00:00+02',15,53000.00,13250.00,'simulation','valid'),
    (8,'2026-06-22 08:15:00+02',15,55000.00,13750.00,'simulation','valid'),
    (8,'2026-06-22 08:30:00+02',15,57000.00,14250.00,'simulation','valid');


-- ============================================================
-- Insert storage specifications
-- ============================================================

INSERT INTO storage_specs(asset_id, energy_capacity_kwh, max_charge_power_kw, max_discharge_power_kw, charge_efficiency_percent, discharge_efficiency_percent, min_state_of_charge_percent, max_state_of_charge_percent)
VALUES
    (4,80000.00,30000.00,30000.00,95.00,95.00,10.00,90.00);