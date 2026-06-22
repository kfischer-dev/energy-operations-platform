INSERT INTO stations (name, station_type, location)
VALUES 
    ('Station A', 'solar_park', 'Stuttgart'),
    ('Station B', 'wind_park', 'Ulm');
    ;

INSERT INTO measurements (station_id, measurement_time, load_value, unit, source, quality_status)
VALUES 
    (1, '2026-06-22 08:15:00', 80.50, 'kW', 'CSV Import', 'valid'),
    (1, '2026-06-22 08:30:00', 95.25, 'kW', 'CSV Import', 'valid'),
    (2, '2026-06-22 08:30:00', 120.75, 'kW', 'CSV Import', 'valid');