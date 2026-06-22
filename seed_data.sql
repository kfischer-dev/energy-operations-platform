INSERT INTO stations (station_name, station_type, station_location)
VALUES
    ('Station A', 'solar_park', 'Stuttgart'),
    ('Station B', 'wind_park', 'Ulm'),
    ('Station C', 'hydro_power', 'Heidelberg'),
    ('Station D', 'battery_storage', 'Karlsruhe'),
    ('Station E', 'substation', 'Waiblingen'),
    ('Station F', 'solar_park', 'Freiburg'),
    ('Station G', 'wind_park', 'Mannheim'),
    ('Station H', 'grid_connection', 'Heilbronn');

INSERT INTO measurements (station_id, measurement_time, load_value, unit, source, quality_status)
VALUES
    (1, '2026-06-22 08:15:00', 80.50, 'kW', 'CSV Import', 'valid'),
    (1, '2026-06-22 08:30:00', 95.25, 'kW', 'CSV Import', 'valid'),
    (1, '2026-06-22 08:45:00', 101.75, 'kW', 'CSV Import', 'valid'),

    (2, '2026-06-22 08:15:00', 120.75, 'kW', 'CSV Import', 'valid'),
    (2, '2026-06-22 08:30:00', 135.20, 'kW', 'CSV Import', 'valid'),
    (2, '2026-06-22 08:45:00', 128.40, 'kW', 'CSV Import', 'valid'),

    (3, '2026-06-22 08:15:00', 210.00, 'kW', 'CSV Import', 'valid'),
    (3, '2026-06-22 08:30:00', 205.50, 'kW', 'CSV Import', 'valid'),
    (3, '2026-06-22 08:45:00', 198.75, 'kW', 'CSV Import', 'valid'),

    (4, '2026-06-22 08:15:00', -45.00, 'kW', 'CSV Import', 'valid'),
    (4, '2026-06-22 08:30:00', -38.50, 'kW', 'CSV Import', 'valid'),
    (4, '2026-06-22 08:45:00', 25.00, 'kW', 'CSV Import', 'valid'),

    (5, '2026-06-22 08:15:00', 450.80, 'kW', 'Sensor API', 'valid'),
    (5, '2026-06-22 08:30:00', 480.30, 'kW', 'Sensor API', 'valid'),
    (5, '2026-06-22 08:45:00', 510.90, 'kW', 'Sensor API', 'valid'),

    (6, '2026-06-22 08:15:00', 60.25, 'kW', 'CSV Import', 'valid'),
    (6, '2026-06-22 08:30:00', 72.40, 'kW', 'CSV Import', 'valid'),
    (6, '2026-06-22 08:45:00', 88.10, 'kW', 'CSV Import', 'valid'),

    (7, '2026-06-22 08:15:00', 155.00, 'kW', 'Sensor API', 'valid'),
    (7, '2026-06-22 08:30:00', 162.75, 'kW', 'Sensor API', 'valid'),
    (7, '2026-06-22 08:45:00', 149.30, 'kW', 'Sensor API', 'valid'),

    (8, '2026-06-22 08:15:00', 720.00, 'kW', 'SCADA', 'valid'),
    (8, '2026-06-22 08:30:00', 760.50, 'kW', 'SCADA', 'valid'),
    (8, '2026-06-22 08:45:00', 790.25, 'kW', 'SCADA', 'valid');