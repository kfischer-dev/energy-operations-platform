import os
from dotenv import load_dotenv
import psycopg
import logging

logger = logging.getLogger(__name__)

# ============================================================
# PostgreSQL Connection Management
# ============================================================

def get_connection():
    """Load database configuration from environment variables and open a PostgreSQL connection."""

    load_dotenv() 

    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")

    logger.info("Connecting to PostgreSQL database...")

    # psycopg.connect() creates a connection to the PostgreSQL database. | It needs the database name, user, password, host and port.
    conn = psycopg.connect(dbname = db_name, user = db_user, password = db_password, host = db_host, port = db_port) # active database connection object
    logger.info("Database connection successful")

    return conn

# ============================================================
# PostgreSQL Read Queries
# ============================================================

def fetch_joined_measurements(conn):
    """Return joined station and measurement data as dictionaries."""

    # The cursor executes SQL statements within the existing database connection.
    with conn.cursor() as cursor: 
        logger.debug("Executing joined measurements query.")
        cursor.execute("""
            SELECT
                stations.station_name,
                measurements.measurement_time,
                measurements.load_value,
                measurements.unit
            FROM measurements
            JOIN stations
                ON measurements.station_id = stations.station_id
            ORDER BY stations.station_name, measurements.measurement_time;
        """)
        rows = cursor.fetchall()

    measurements = []
    for row in rows:
        measurement = map_measurement_row(row)
        measurements.append(measurement)

    return measurements

def fetch_stations(conn):
    """Return all stations from the database as dictionaries."""

    with conn.cursor() as cursor: 
        logger.debug("Executing station query.")
        cursor.execute("""
            SELECT
                station_id,
                station_name,
                station_type,
                station_location
            FROM stations
            ORDER BY station_id;
        """)
        rows = cursor.fetchall()
    
    stations = []
    for row in rows:
        station = map_station_row(row)
        stations.append(station)
    
    return stations

def fetch_measurements_by_station_id(conn, station_id):
    """Return all measurements for a specific station as dictionaries."""

    with conn.cursor() as cursor: 
        logger.debug("Executing joined measurements by station_id query.")

        # Use a parameterized query instead of string formatting to keep SQL execution safe.
        cursor.execute("""
            SELECT
                s.station_name,
                m.measurement_time,
                m.load_value,
                m.unit
            FROM measurements m
            JOIN stations s
                ON m.station_id = s.station_id
            WHERE s.station_id = %s
            ORDER BY s.station_name, m.measurement_time;
        """, (station_id,))
        rows = cursor.fetchall()

    measurements = []
    for row in rows:
        measurement = map_measurement_row(row)
        measurements.append(measurement)

    return measurements

def fetch_station_by_id(conn, station_id):
    """Return one station by ID, or None if the station does not exist."""

    with conn.cursor() as cursor:
        logger.debug("Executing station query.")
        cursor.execute("""
            SELECT
                station_id,
                station_name,
                station_type,
                station_location
            FROM stations
            WHERE station_id = %s;
        """, (station_id,))

        row = cursor.fetchone()

        if row is None:
            return None

        return map_station_row(row)

# ============================================================
# Station Mapping
# ============================================================
def map_station_row(row):

    station_id, station_name, station_type, station_location = row

    station = {"station_id": station_id, "station_name": station_name, "station_type": station_type, "station_location": station_location}

    return station

# ============================================================
# Measurement Mapping
# ============================================================
def map_measurement_row(row):

    station_name, measurement_time, load_value, unit = row

    measurement = {"station_name": station_name, "measurement_time": measurement_time, "load_value": load_value, "unit": unit}

    return measurement

# ============================================================
# Database Report Data Loader
# ============================================================

def fetch_database_report_data():
    conn = get_connection() 

    logger.info("Loading database report data started.")

    try:
        station_data = fetch_stations(conn) 
        logger.info(f"Loaded {len(station_data)} stations from database.")
        measurement_data = fetch_joined_measurements(conn) 
        logger.info(f"Loaded {len(measurement_data)} joined measurements from database.")

    finally:
        conn.close() 
        logger.info("Database connection closed.")

    return station_data, measurement_data
