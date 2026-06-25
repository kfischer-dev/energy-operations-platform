import os
from dotenv import load_dotenv
import psycopg
import logging

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

def fetch_joined_measurements(conn):
    cursor = conn.cursor() # conn.cursor() creates a cursor object. The cursor is used to execute SQL commands through the database connection.

    # cursor.execute() sends an SQL command to PostgreSQL. For example, it can execute a SELECT query.
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

    # fetchall() retrieves all result rows from the last executed SELECT query.
    rows = cursor.fetchall()

    cursor.close()

    return rows



