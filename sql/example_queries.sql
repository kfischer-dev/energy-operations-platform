-- Show assets table
SELECT * FROM assets;

-- Show measurements table
SELECT * FROM measurements;

-- Filter measurements for a specific asset
SELECT * FROM measurements WHERE asset_id = 1;

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

-- Filter measurements by asset type
SELECT
    assets.asset_name,
    measurements.measurement_time,
    measurements.load_value,
    measurements.unit
FROM measurements -- Start with the measurements table
JOIN assets -- Join the assets table
    ON measurements.asset_id = assets.asset_id
WHERE asset_type = 'wind_park';

-- Filter joined asset and measurement data
SELECT
    assets.asset_name,
    measurements.measurement_time,
    measurements.load_value,
    measurements.unit
FROM measurements -- Start with the measurements table
JOIN assets -- Join the assets table
    ON measurements.asset_id = assets.asset_id
ORDER BY assets.asset_name, measurements.measurement_time;

-- Filter joined asset and measurement data above a load threshold
SELECT
    assets.asset_name,
    assets.asset_type,
    measurements.measurement_time,
    measurements.load_value,
    measurements.unit
FROM measurements
JOIN assets
    ON measurements.asset_id = assets.asset_id
WHERE measurements.load_value > 150
ORDER BY measurements.load_value DESC;

-- Show only assets with an average load above 150
SELECT
    assets.asset_name,
    COUNT(measurements.measurement_id) AS number_of_measurements,
    ROUND(AVG(measurements.load_value), 2) AS average_load,
    MIN(measurements.load_value) AS min_load,
    MAX(measurements.load_value) AS max_load
FROM assets
JOIN measurements
    ON assets.asset_id = measurements.asset_id
GROUP BY assets.asset_name
HAVING AVG(measurements.load_value) > 150
ORDER BY average_load DESC;

-- Summary statistics per asset
-- Shows number of measurements, average load, minimum load and maximum load per asset.
SELECT
    assets.asset_name,
    COUNT(measurements.measurement_id) AS number_of_measurements,
    ROUND(AVG(measurements.load_value), 2) AS average_load,
    MIN(measurements.load_value) AS min_load,
    MAX(measurements.load_value) AS max_load
FROM assets -- Start with the assets table
JOIN measurements -- Join the measurements table
    ON assets.asset_id = measurements.asset_id
GROUP BY assets.asset_name
ORDER BY average_load ASC;

