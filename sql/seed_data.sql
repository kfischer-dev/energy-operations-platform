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


INSERT INTO simulation_runs(simulation_mode, start_time, end_time, interval_minutes, random_seed, status, generated_measurement_count, created_at, started_at, completed_at)
VALUES
    ('historical', '2026-06-22 08:00:00+02', '2026-06-22 09:00:00+02', 15, 42, 'completed', 64, '2026-06-22 07:59:00+02', '2026-06-22 08:00:00+02', '2026-06-22 09:00:00+02');


INSERT INTO measurements(asset_id, simulation_run_id, measurement_time, active_power_kw, source, quality_status)
VALUES
    -- North: North Sea Wind Park
    (1,1,'2026-06-22 08:00:00+02',80000,'simulation','valid'),
    (1,1,'2026-06-22 08:15:00+02',84000,'simulation','valid'),
    (1,1,'2026-06-22 08:30:00+02',79000,'simulation','valid'),
    (1,1,'2026-06-22 08:45:00+02',86000,'simulation','valid'),

    -- North: Solar Park Schleswig-Holstein
    (2,1,'2026-06-22 08:00:00+02',12000,'simulation','valid'),
    (2,1,'2026-06-22 08:15:00+02',15000,'simulation','valid'),
    (2,1,'2026-06-22 08:30:00+02',18500,'simulation','valid'),
    (2,1,'2026-06-22 08:45:00+02',22000,'simulation','valid'),

    -- North: City Load Hamburg
    (3,1,'2026-06-22 08:00:00+02',138000,'simulation','valid'),
    (3,1,'2026-06-22 08:15:00+02',143000,'simulation','valid'),
    (3,1,'2026-06-22 08:30:00+02',149000,'simulation','valid'),
    (3,1,'2026-06-22 08:45:00+02',153000,'simulation','valid'),

    -- North: Substation Hamburg, regional import
    (4,1,'2026-06-22 08:00:00+02',46000,'simulation','valid'),
    (4,1,'2026-06-22 08:15:00+02',44000,'simulation','valid'),
    (4,1,'2026-06-22 08:30:00+02',51500,'simulation','valid'),
    (4,1,'2026-06-22 08:45:00+02',45000,'simulation','valid'),

    -- South: Hydro Power Plant Black Forest
    (5,1,'2026-06-22 08:00:00+02',68000,'simulation','valid'),
    (5,1,'2026-06-22 08:15:00+02',69000,'simulation','valid'),
    (5,1,'2026-06-22 08:30:00+02',71000,'simulation','valid'),
    (5,1,'2026-06-22 08:45:00+02',70000,'simulation','valid'),

    -- South: Solar Park Ulm
    (6,1,'2026-06-22 08:00:00+02',12000,'simulation','valid'),
    (6,1,'2026-06-22 08:15:00+02',16000,'simulation','valid'),
    (6,1,'2026-06-22 08:30:00+02',20000,'simulation','valid'),
    (6,1,'2026-06-22 08:45:00+02',24000,'simulation','valid'),

    -- South: Battery Storage Stuttgart, discharging
    (7,1,'2026-06-22 08:00:00+02',15000,'simulation','valid'),
    (7,1,'2026-06-22 08:15:00+02',12000,'simulation','valid'),
    (7,1,'2026-06-22 08:30:00+02',8000,'simulation','valid'),
    (7,1,'2026-06-22 08:45:00+02',5000,'simulation','valid'),

    -- South: Industrial Load Stuttgart
    (8,1,'2026-06-22 08:00:00+02',92000,'simulation','valid'),
    (8,1,'2026-06-22 08:15:00+02',97000,'simulation','valid'),
    (8,1,'2026-06-22 08:30:00+02',102000,'simulation','valid'),
    (8,1,'2026-06-22 08:45:00+02',105000,'simulation','valid'),

    -- East: Solar Park Brandenburg
    (9,1,'2026-06-22 08:00:00+02',18000,'simulation','valid'),
    (9,1,'2026-06-22 08:15:00+02',22500,'simulation','valid'),
    (9,1,'2026-06-22 08:30:00+02',27000,'simulation','valid'),
    (9,1,'2026-06-22 08:45:00+02',32000,'simulation','valid'),

    -- East: Biomass Power Plant Brandenburg
    (10,1,'2026-06-22 08:00:00+02',42000,'simulation','valid'),
    (10,1,'2026-06-22 08:15:00+02',42500,'simulation','valid'),
    (10,1,'2026-06-22 08:30:00+02',43000,'simulation','valid'),
    (10,1,'2026-06-22 08:45:00+02',42800,'simulation','valid'),

    -- East: Residential Load Berlin
    (11,1,'2026-06-22 08:00:00+02',112000,'simulation','valid'),
    (11,1,'2026-06-22 08:15:00+02',118000,'simulation','valid'),
    (11,1,'2026-06-22 08:30:00+02',121000,'simulation','valid'),
    (11,1,'2026-06-22 08:45:00+02',116000,'simulation','valid'),

    -- East: Substation Berlin, regional import
    (12,1,'2026-06-22 08:00:00+02',52000,'simulation','valid'),
    (12,1,'2026-06-22 08:15:00+02',53000,'simulation','valid'),
    (12,1,'2026-06-22 08:30:00+02',51000,'simulation','valid'),
    (12,1,'2026-06-22 08:45:00+02',41200,'simulation','valid'),

    -- West: Gas Power Plant Rhine-Ruhr
    (13,1,'2026-06-22 08:00:00+02',105000,'simulation','valid'),
    (13,1,'2026-06-22 08:15:00+02',112000,'simulation','valid'),
    (13,1,'2026-06-22 08:30:00+02',120000,'simulation','valid'),
    (13,1,'2026-06-22 08:45:00+02',128000,'simulation','valid'),

    -- West: Wind Park Sauerland
    (14,1,'2026-06-22 08:00:00+02',36000,'simulation','valid'),
    (14,1,'2026-06-22 08:15:00+02',39000,'simulation','valid'),
    (14,1,'2026-06-22 08:30:00+02',37500,'simulation','valid'),
    (14,1,'2026-06-22 08:45:00+02',41000,'simulation','valid'),

    -- West: Industrial Load Ruhr
    (15,1,'2026-06-22 08:00:00+02',132000,'simulation','valid'),
    (15,1,'2026-06-22 08:15:00+02',139000,'simulation','valid'),
    (15,1,'2026-06-22 08:30:00+02',145000,'simulation','valid'),
    (15,1,'2026-06-22 08:45:00+02',148000,'simulation','valid'),

    -- West: Data Center Düsseldorf
    (16,1,'2026-06-22 08:00:00+02',62000,'simulation','valid'),
    (16,1,'2026-06-22 08:15:00+02',62500,'simulation','valid'),
    (16,1,'2026-06-22 08:30:00+02',63000,'simulation','valid'),
    (16,1,'2026-06-22 08:45:00+02',62800,'simulation','valid');


INSERT INTO storage_specs(asset_id, energy_capacity_kwh, max_charge_power_kw, max_discharge_power_kw, charge_efficiency_percent, discharge_efficiency_percent, min_state_of_charge_percent, max_state_of_charge_percent)
VALUES
    (7,80000,30000,30000,95.00,95.00,10.00,90.00);
