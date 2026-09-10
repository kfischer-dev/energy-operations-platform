INSERT INTO regions(region_code, region_prefix, region_name, region_description)
VALUES
    ('DE-NORTH','N','Northern Germany','Region covering the northern part of Germany'),
    ('DE-SOUTH','S','Southern Germany','Region covering the southern part of Germany'),
    ('DE-EAST','E','Eastern Germany','Region covering the eastern part of Germany'),
    ('DE-WEST','W','Western Germany','Region covering the western part of Germany');


INSERT INTO asset_types(asset_type_name, asset_prefix, asset_role, is_renewable, is_weather_dependent, is_dispatchable, can_store_energy)
VALUES
    -- Producers
    ('solar_park','SOLAR','producer',TRUE,TRUE,FALSE,FALSE),
    ('wind_park','WIND','producer',TRUE,TRUE,FALSE,FALSE),
    ('hydro_power_plant','HYDRO','producer',TRUE,TRUE,TRUE,FALSE),
    ('gas_power_plant','GAS','producer',FALSE,FALSE,TRUE,FALSE),
    ('biomass_power_plant','BIO','producer',TRUE,FALSE,TRUE,FALSE),

    -- Storage
    ('battery_storage','BESS','storage',FALSE,FALSE,TRUE,TRUE),

    -- Grid infrastructure
    ('substation','SUB','grid',FALSE,FALSE,FALSE,FALSE),

    -- Consumers
    ('residential_load','RES','consumer',FALSE,FALSE,FALSE,FALSE),
    ('commercial_load','COM','consumer',FALSE,FALSE,FALSE,FALSE),
    ('industrial_load','IND','consumer',FALSE,FALSE,FALSE,FALSE),
    ('city_load','CITY','consumer',FALSE,FALSE,FALSE,FALSE),
    ('ev_charging_park','EV','consumer',FALSE,FALSE,FALSE,FALSE),
    ('data_center','DC','consumer',FALSE,FALSE,FALSE,FALSE);


INSERT INTO assets(asset_code, asset_name, asset_location, rated_power_kw, operating_status, latitude, longitude, asset_type_id, region_id)
VALUES
    -- Northern Germany
    ('N-WIND-001','North Sea Wind Park','North Sea',120000,'online',54.500000,7.500000,2,1),
    ('N-SOLAR-001','Solar Park Schleswig-Holstein','Schleswig-Holstein',40000,'online',54.200000,9.500000,1,1),
    ('N-CITY-001','City Load Hamburg','Hamburg',180000,'online',53.551086,9.993682,11,1),
    ('N-SUB-001','Substation Hamburg','Hamburg',250000,'online',53.500000,10.100000,7,1),

    -- Southern Germany
    ('S-HYDRO-001','Hydro Power Plant Black Forest','Baden-Württemberg',80000,'online',47.900000,8.100000,3,2),
    ('S-SOLAR-001','Solar Park Ulm','Baden-Württemberg',35000,'online',48.401082,9.987608,1,2),
    ('S-BESS-001','Battery Storage Stuttgart','Baden-Württemberg',30000,'online',48.775846,9.182932,6,2),
    ('S-IND-001','Industrial Load Stuttgart','Baden-Württemberg',130000,'online',48.750000,9.300000,10,2),

    -- Eastern Germany
    ('E-SOLAR-001','Solar Park Brandenburg','Brandenburg',50000,'online',52.400000,13.000000,1,3),
    ('E-BIO-001','Biomass Power Plant Brandenburg','Brandenburg',50000,'online',52.300000,13.500000,5,3),
    ('E-RES-001','Residential Load Berlin','Berlin',150000,'online',52.520008,13.404954,8,3),
    ('E-SUB-001','Substation Berlin','Berlin',220000,'online',52.480000,13.450000,7,3),

    -- Western Germany
    ('W-GAS-001','Gas Power Plant Rhine-Ruhr','North Rhine-Westphalia',180000,'online',51.450000,7.000000,4,4),
    ('W-WIND-001','Wind Park Sauerland','North Rhine-Westphalia',60000,'online',51.200000,8.000000,2,4),
    ('W-IND-001','Industrial Load Ruhr','North Rhine-Westphalia',200000,'online',51.480000,7.200000,10,4),
    ('W-DC-001','Data Center Düsseldorf','North Rhine-Westphalia',80000,'online',51.227741,6.773456,13,4);

-- ============================================================
-- Frontend demo data
-- ============================================================
-- Purpose:
-- - one complete 24-hour demo period for the React dashboard
-- - 15-minute point-in-time measurements (97 points per asset)
-- - deterministic but visually distinct producer/consumer profiles
-- - enough data for balance series, energy mix and KPI cards
--
-- Recommended frontend demo period:
--   start_time = 2026-09-01T00:00:00+02:00
--   end_time   = 2026-09-02T00:00:00+02:00
--   interval_minutes = 15
--
-- The seed intentionally focuses the time-series data on producer and
-- consumer assets. Storage/grid assets remain available in /assets but
-- are not part of the production/consumption balance.
-- ============================================================

INSERT INTO simulation_runs(
    simulation_mode,
    start_time,
    end_time,
    interval_minutes,
    random_seed,
    status,
    generated_measurement_count,
    created_at,
    started_at,
    completed_at
)
VALUES (
    'historical',
    '2026-09-01 00:00:00+02',
    '2026-09-02 00:00:00+02',
    15,
    42,
    'completed',
    1261,
    '2026-08-31 23:59:00+02',
    '2026-09-01 00:00:00+02',
    '2026-09-02 00:00:00+02'
);

WITH demo_points AS (
    SELECT
        measurement_time,
        EXTRACT(HOUR FROM measurement_time)
            + EXTRACT(MINUTE FROM measurement_time) / 60.0 AS hour_of_day
    FROM generate_series(
        '2026-09-01 00:00:00+02'::timestamptz,
        '2026-09-02 00:00:00+02'::timestamptz,
        interval '15 minutes'
    ) AS measurement_time
),
demo_assets AS (
    SELECT asset_id, asset_code
    FROM assets
    WHERE asset_code IN (
        'N-WIND-001',
        'N-SOLAR-001',
        'N-CITY-001',
        'S-HYDRO-001',
        'S-SOLAR-001',
        'S-IND-001',
        'E-SOLAR-001',
        'E-BIO-001',
        'E-RES-001',
        'W-GAS-001',
        'W-WIND-001',
        'W-IND-001',
        'W-DC-001'
    )
),
demo_values AS (
    SELECT
        a.asset_id,
        a.asset_code,
        p.measurement_time,
        p.hour_of_day,
        CASE a.asset_code
            -- Producers -----------------------------------------------------
            WHEN 'N-WIND-001' THEN
                81000
                + 9000 * SIN(2 * PI() * p.hour_of_day / 24.0)
                + 4500 * SIN(2 * PI() * p.hour_of_day / 6.0)

            WHEN 'W-WIND-001' THEN
                39000
                + 6500 * SIN(2 * PI() * (p.hour_of_day + 2.0) / 24.0)
                + 3000 * SIN(2 * PI() * p.hour_of_day / 8.0)

            WHEN 'N-SOLAR-001' THEN
                CASE
                    WHEN p.hour_of_day BETWEEN 6 AND 20
                    THEN 34000 * SIN(PI() * (p.hour_of_day - 6) / 14.0)
                    ELSE 0
                END

            WHEN 'S-SOLAR-001' THEN
                CASE
                    WHEN p.hour_of_day BETWEEN 6 AND 20
                    THEN 31500 * SIN(PI() * (p.hour_of_day - 6) / 14.0)
                    ELSE 0
                END

            WHEN 'E-SOLAR-001' THEN
                CASE
                    WHEN p.hour_of_day BETWEEN 6 AND 20
                    THEN 44500 * SIN(PI() * (p.hour_of_day - 6) / 14.0)
                    ELSE 0
                END

            WHEN 'S-HYDRO-001' THEN
                70000 + 1800 * SIN(2 * PI() * (p.hour_of_day - 4.0) / 24.0)

            WHEN 'E-BIO-001' THEN
                42000 + 900 * SIN(2 * PI() * p.hour_of_day / 12.0)

            WHEN 'W-GAS-001' THEN
                CASE
                    WHEN p.hour_of_day < 6 THEN 70000
                    WHEN p.hour_of_day < 9 THEN 70000 + (p.hour_of_day - 6) * 15000
                    WHEN p.hour_of_day < 17 THEN 115000
                    WHEN p.hour_of_day < 21 THEN 115000 + (p.hour_of_day - 17) * 5000
                    ELSE 135000 - (p.hour_of_day - 21) * 18000
                END

            -- Consumers -----------------------------------------------------
            WHEN 'N-CITY-001' THEN
                72000
                + 43000 * EXP(-POWER((p.hour_of_day - 8.0) / 2.3, 2))
                + 70000 * EXP(-POWER((p.hour_of_day - 19.0) / 2.8, 2))
                + 18000 * EXP(-POWER((p.hour_of_day - 13.0) / 4.5, 2))

            WHEN 'S-IND-001' THEN
                CASE
                    WHEN p.hour_of_day < 6 THEN 50000
                    WHEN p.hour_of_day < 8 THEN 50000 + (p.hour_of_day - 6) * 26000
                    WHEN p.hour_of_day < 17 THEN 102000 + 4000 * SIN(2 * PI() * (p.hour_of_day - 8) / 9.0)
                    WHEN p.hour_of_day < 20 THEN 102000 - (p.hour_of_day - 17) * 17000
                    ELSE 51000
                END

            WHEN 'W-IND-001' THEN
                CASE
                    WHEN p.hour_of_day < 6 THEN 76000
                    WHEN p.hour_of_day < 8 THEN 76000 + (p.hour_of_day - 6) * 40000
                    WHEN p.hour_of_day < 17 THEN 156000 + 7000 * SIN(2 * PI() * (p.hour_of_day - 8) / 9.0)
                    WHEN p.hour_of_day < 20 THEN 156000 - (p.hour_of_day - 17) * 26000
                    ELSE 78000
                END

            WHEN 'E-RES-001' THEN
                50000
                + 42000 * EXP(-POWER((p.hour_of_day - 7.5) / 1.8, 2))
                + 76000 * EXP(-POWER((p.hour_of_day - 20.0) / 2.6, 2))

            WHEN 'W-DC-001' THEN
                63000
                + 1800 * SIN(2 * PI() * (p.hour_of_day - 3.0) / 24.0)
                + 900 * SIN(2 * PI() * p.hour_of_day / 6.0)
        END AS active_power_kw
    FROM demo_assets a
    CROSS JOIN demo_points p
)
INSERT INTO measurements(
    asset_id,
    simulation_run_id,
    measurement_time,
    active_power_kw,
    source,
    quality_status
)
SELECT
    asset_id,
    1,
    measurement_time,
    ROUND(GREATEST(active_power_kw, 0)::numeric, 2),
    'simulation',
    'valid'
FROM demo_values
ORDER BY asset_id, measurement_time;


INSERT INTO storage_specs(asset_id, energy_capacity_kwh, max_charge_power_kw, max_discharge_power_kw, charge_efficiency_percent, discharge_efficiency_percent, min_state_of_charge_percent, max_state_of_charge_percent)
VALUES
    (7,80000,30000,30000,95.00,95.00,10.00,90.00);
