-- Show stations table
SELECT * FROM stations;

-- Show measurements table
SELECT * FROM measurements;

-- Filter measurements for a specific station
SELECT * FROM measurements WHERE station_id = 1;

-- Filter measurements above a load threshold
SELECT * FROM measurements
WHERE load_value > 150;

-- Filter measurements by data source
SELECT * FROM measurements
WHERE source = 'Sensor API';

-- Filter measurements from Sensor API above a load threshold
SELECT *
FROM measurements
WHERE source = 'Sensor API'
  AND load_value > 400;

-- Filter measurements from Sensor API or SCADA
SELECT *
FROM measurements
WHERE source = 'Sensor API'
   OR source = 'SCADA';

-- Filter measurements by station type
SELECT
    stations.station_name,
    measurements.measurement_time,
    measurements.load_value,
    measurements.unit
FROM measurements -- Start with the measurements table
JOIN stations -- Join the stations table
    ON measurements.station_id = stations.station_id
WHERE station_type = 'wind_park';

-- Filter joined station and measurement data
SELECT
    stations.station_name,
    measurements.measurement_time,
    measurements.load_value,
    measurements.unit
FROM measurements -- Start with the measurements table
JOIN stations -- Join the stations table
    ON measurements.station_id = stations.station_id
ORDER BY stations.station_name, measurements.measurement_time;

-- Filter joined station and measurement data above a load threshold
SELECT
    stations.station_name,
    stations.station_type,
    measurements.measurement_time,
    measurements.load_value,
    measurements.unit
FROM measurements
JOIN stations
    ON measurements.station_id = stations.station_id
WHERE measurements.load_value > 150
ORDER BY measurements.load_value DESC;

-- Show only stations with an average load above 150
SELECT
    stations.station_name,
    COUNT(measurements.measurement_id) AS number_of_measurements,
    ROUND(AVG(measurements.load_value), 2) AS average_load,
    MIN(measurements.load_value) AS min_load,
    MAX(measurements.load_value) AS max_load
FROM stations
JOIN measurements
    ON stations.station_id = measurements.station_id
GROUP BY stations.station_name
HAVING AVG(measurements.load_value) > 150
ORDER BY average_load DESC;

-- Summary statistics per station
-- Shows number of measurements, average load, minimum load and maximum load per station.
SELECT
    stations.station_name,
    COUNT(measurements.measurement_id) AS number_of_measurements,
    ROUND(AVG(measurements.load_value), 2) AS average_load,
    MIN(measurements.load_value) AS min_load,
    MAX(measurements.load_value) AS max_load
FROM stations -- Start with the stations table
JOIN measurements -- Join the measurements table
    ON stations.station_id = measurements.station_id
GROUP BY stations.station_name
ORDER BY average_load ASC;

