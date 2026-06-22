SELECT * FROM stations;

SELECT * FROM measurements;

SELECT * FROM measurements WHERE station_id = 1;

SELECT
    stations.name,
    measurements.measurement_time,
    measurements.load_value,
    measurements.unit
FROM measurements
JOIN stations
    ON measurements.station_id = stations.station_id
ORDER BY stations.name, measurements.measurement_time;