import os
from dotenv import load_dotenv
import psycopg
import logging

# ============================================================
# PostgreSQL Connection Management
# ============================================================

def get_connection():

    load_dotenv() # loads the values from the local .env file into the environment of the running Python program. This makes variables like DB_NAME, DB_USER and DB_PASSWORD available.

    # os.getenv() reads a specific environment variable. Example: os.getenv("DB_NAME") reads the value of DB_NAME.
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")

    logging.info("Connecting to PostgreSQL database...")

    # psycopg.connect() creates a connection to the PostgreSQL database. | It needs the database name, user, password, host and port.
    conn = psycopg.connect(dbname = db_name, user = db_user, password = db_password, host = db_host, port = db_port) # conn is the active database connection object. It represents the open connection between Python and PostgreSQL.

    logging.info("Database connection successful")

    return conn

# ============================================================
# PostgreSQL Read Queries
# ============================================================

def fetch_joined_measurements(conn):

    with conn.cursor() as cursor: # cursor to execute SQL commands through the database connection
        logging.debug("Executing joined measurements query.")
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

    with conn.cursor() as cursor: # cursor to execute SQL commands through the database connection
        logging.debug("Executing station query.")
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
    conn = get_connection() # Object for active database connection

    logging.info("Loading database report data started.")

    try:
        station_data = fetch_stations(conn) # Values of database
        logging.info(f"Loaded {len(station_data)} stations from database.")
        measurement_data = fetch_joined_measurements(conn) # Values of database
        logging.info(f"Loaded {len(measurement_data)} joined measurements from database.")

    finally:
        conn.close() # Close Database connection
        logging.info("Database connection closed.")

    return station_data, measurement_data
