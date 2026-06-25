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

    return rows

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
    
    return rows

# ============================================================
# Database Report Data Loader
# ============================================================

def fetch_database_report_data():
    conn = get_connection() # Object for active database connection

    logging.info("Loading database report data started.")

    try:
        station_rows = fetch_stations(conn) # Values of database
        logging.info(f"Loaded {len(station_rows)} stations from database.")
        measurement_rows = fetch_joined_measurements(conn) # Values of database
        logging.info(f"Loaded {len(measurement_rows)} joined measurements from database.")

    finally:
        conn.close() # Close Database connection
        logging.info("Database connection closed.")

    return station_rows, measurement_rows

