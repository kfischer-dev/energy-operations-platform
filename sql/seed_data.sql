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

INSERT INTO measurements(asset_id, measurement_time, interval_minutes, active_power_kw, energy_kwh, source, quality_status)
VALUES
    -- North: North Sea Wind Park
    (1,'2026-06-22 08:00:00+02',15,80000,20000,'simulation','valid'),
    (1,'2026-06-22 08:15:00+02',15,84000,21000,'simulation','valid'),
    (1,'2026-06-22 08:30:00+02',15,79000,19750,'simulation','valid'),
    (1,'2026-06-22 08:45:00+02',15,86000,21500,'simulation','valid'),

    -- North: Solar Park Schleswig-Holstein
    (2,'2026-06-22 08:00:00+02',15,12000,3000,'simulation','valid'),
    (2,'2026-06-22 08:15:00+02',15,15000,3750,'simulation','valid'),
    (2,'2026-06-22 08:30:00+02',15,18500,4625,'simulation','valid'),
    (2,'2026-06-22 08:45:00+02',15,22000,5500,'simulation','valid'),

    -- North: City Load Hamburg
    (3,'2026-06-22 08:00:00+02',15,138000,34500,'simulation','valid'),
    (3,'2026-06-22 08:15:00+02',15,143000,35750,'simulation','valid'),
    (3,'2026-06-22 08:30:00+02',15,149000,37250,'simulation','valid'),
    (3,'2026-06-22 08:45:00+02',15,153000,38250,'simulation','valid'),

    -- North: Substation Hamburg, regional import
    (4,'2026-06-22 08:00:00+02',15,46000,11500,'simulation','valid'),
    (4,'2026-06-22 08:15:00+02',15,44000,11000,'simulation','valid'),
    (4,'2026-06-22 08:30:00+02',15,51500,12875,'simulation','valid'),
    (4,'2026-06-22 08:45:00+02',15,45000,11250,'simulation','valid'),

    -- South: Hydro Power Plant Black Forest
    (5,'2026-06-22 08:00:00+02',15,68000,17000,'simulation','valid'),
    (5,'2026-06-22 08:15:00+02',15,69000,17250,'simulation','valid'),
    (5,'2026-06-22 08:30:00+02',15,71000,17750,'simulation','valid'),
    (5,'2026-06-22 08:45:00+02',15,70000,17500,'simulation','valid'),

    -- South: Solar Park Ulm
    (6,'2026-06-22 08:00:00+02',15,12000,3000,'simulation','valid'),
    (6,'2026-06-22 08:15:00+02',15,16000,4000,'simulation','valid'),
    (6,'2026-06-22 08:30:00+02',15,20000,5000,'simulation','valid'),
    (6,'2026-06-22 08:45:00+02',15,24000,6000,'simulation','valid'),

    -- South: Battery Storage Stuttgart, discharging
    (7,'2026-06-22 08:00:00+02',15,15000,3750,'simulation','valid'),
    (7,'2026-06-22 08:15:00+02',15,12000,3000,'simulation','valid'),
    (7,'2026-06-22 08:30:00+02',15,8000,2000,'simulation','valid'),
    (7,'2026-06-22 08:45:00+02',15,5000,1250,'simulation','valid'),

    -- South: Industrial Load Stuttgart
    (8,'2026-06-22 08:00:00+02',15,92000,23000,'simulation','valid'),
    (8,'2026-06-22 08:15:00+02',15,97000,24250,'simulation','valid'),
    (8,'2026-06-22 08:30:00+02',15,102000,25500,'simulation','valid'),
    (8,'2026-06-22 08:45:00+02',15,105000,26250,'simulation','valid'),

    -- East: Solar Park Brandenburg
    (9,'2026-06-22 08:00:00+02',15,18000,4500,'simulation','valid'),
    (9,'2026-06-22 08:15:00+02',15,22500,5625,'simulation','valid'),
    (9,'2026-06-22 08:30:00+02',15,27000,6750,'simulation','valid'),
    (9,'2026-06-22 08:45:00+02',15,32000,8000,'simulation','valid'),

    -- East: Biomass Power Plant Brandenburg
    (10,'2026-06-22 08:00:00+02',15,42000,10500,'simulation','valid'),
    (10,'2026-06-22 08:15:00+02',15,42500,10625,'simulation','valid'),
    (10,'2026-06-22 08:30:00+02',15,43000,10750,'simulation','valid'),
    (10,'2026-06-22 08:45:00+02',15,42800,10700,'simulation','valid'),

    -- East: Residential Load Berlin
    (11,'2026-06-22 08:00:00+02',15,112000,28000,'simulation','valid'),
    (11,'2026-06-22 08:15:00+02',15,118000,29500,'simulation','valid'),
    (11,'2026-06-22 08:30:00+02',15,121000,30250,'simulation','valid'),
    (11,'2026-06-22 08:45:00+02',15,116000,29000,'simulation','valid'),

    -- East: Substation Berlin, regional import
    (12,'2026-06-22 08:00:00+02',15,52000,13000,'simulation','valid'),
    (12,'2026-06-22 08:15:00+02',15,53000,13250,'simulation','valid'),
    (12,'2026-06-22 08:30:00+02',15,51000,12750,'simulation','valid'),
    (12,'2026-06-22 08:45:00+02',15,41200,10300,'simulation','valid'),

    -- West: Gas Power Plant Rhine-Ruhr
    (13,'2026-06-22 08:00:00+02',15,105000,26250,'simulation','valid'),
    (13,'2026-06-22 08:15:00+02',15,112000,28000,'simulation','valid'),
    (13,'2026-06-22 08:30:00+02',15,120000,30000,'simulation','valid'),
    (13,'2026-06-22 08:45:00+02',15,128000,32000,'simulation','valid'),

    -- West: Wind Park Sauerland
    (14,'2026-06-22 08:00:00+02',15,36000,9000,'simulation','valid'),
    (14,'2026-06-22 08:15:00+02',15,39000,9750,'simulation','valid'),
    (14,'2026-06-22 08:30:00+02',15,37500,9375,'simulation','valid'),
    (14,'2026-06-22 08:45:00+02',15,41000,10250,'simulation','valid'),

    -- West: Industrial Load Ruhr
    (15,'2026-06-22 08:00:00+02',15,132000,33000,'simulation','valid'),
    (15,'2026-06-22 08:15:00+02',15,139000,34750,'simulation','valid'),
    (15,'2026-06-22 08:30:00+02',15,145000,36250,'simulation','valid'),
    (15,'2026-06-22 08:45:00+02',15,148000,37000,'simulation','valid'),

    -- West: Data Center Düsseldorf
    (16,'2026-06-22 08:00:00+02',15,62000,15500,'simulation','valid'),
    (16,'2026-06-22 08:15:00+02',15,62500,15625,'simulation','valid'),
    (16,'2026-06-22 08:30:00+02',15,63000,15750,'simulation','valid'),
    (16,'2026-06-22 08:45:00+02',15,62800,15700,'simulation','valid');

INSERT INTO storage_specs(asset_id, energy_capacity_kwh, max_charge_power_kw, max_discharge_power_kw, charge_efficiency_percent, discharge_efficiency_percent, min_state_of_charge_percent, max_state_of_charge_percent)
VALUES
    (7,80000,30000,30000,95.00,95.00,10.00,90.00);