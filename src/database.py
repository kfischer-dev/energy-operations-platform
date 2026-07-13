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
    """Return joined asset and measurement data as dictionaries."""

    # The cursor executes SQL statements within the existing database connection.
    with conn.cursor() as cursor: 
        logger.debug("Executing joined measurements query.")
        cursor.execute("""
            SELECT
                assets.asset_name,
                measurements.measurement_time,
                measurements.load_value,
                measurements.unit
            FROM measurements
            JOIN assets
                ON measurements.asset_id = assets.asset_id
            ORDER BY assets.asset_name, measurements.measurement_time;
        """)
        rows = cursor.fetchall()

    measurements = []
    for row in rows:
        measurement = map_measurement_row(row)
        measurements.append(measurement)

    return measurements

def fetch_assets(conn):
    """Return all assets from the database as dictionaries."""

    with conn.cursor() as cursor: 
        logger.debug("Executing asset query.")
        cursor.execute("""
            SELECT
                asset_id,
                asset_name,
                asset_type,
                asset_location
            FROM assets
            ORDER BY asset_id;
        """)
        rows = cursor.fetchall()
    
    assets = []
    for row in rows:
        asset = map_asset_row(row)
        assets.append(asset)
    
    return assets

def fetch_measurements_by_asset_id(conn, asset_id):
    """Return all measurements for a specific asset as dictionaries."""

    with conn.cursor() as cursor: 
        logger.debug("Executing joined measurements by asset_id query.")

        # Use a parameterized query instead of string formatting to keep SQL execution safe.
        cursor.execute("""
            SELECT
                s.asset_name,
                m.measurement_time,
                m.load_value,
                m.unit
            FROM measurements m
            JOIN assets s
                ON m.asset_id = s.asset_id
            WHERE s.asset_id = %s
            ORDER BY s.asset_name, m.measurement_time;
        """, (asset_id,))
        rows = cursor.fetchall()

    measurements = []
    for row in rows:
        measurement = map_measurement_row(row)
        measurements.append(measurement)

    return measurements

def fetch_asset_by_id(conn, asset_id):
    """Return one asset by ID, or None if the asset does not exist."""

    with conn.cursor() as cursor:
        logger.debug("Executing asset query.")
        cursor.execute("""
            SELECT
                asset_id,
                asset_name,
                asset_type,
                asset_location
            FROM assets
            WHERE asset_id = %s;
        """, (asset_id,))

        row = cursor.fetchone()

        if row is None:
            return None

        return map_asset_row(row)
    
def fetch_measurement_by_id(conn, measurement_id):
    """Return measurements of a specific measurement id as dictionary."""

    with conn.cursor() as cursor:
        logger.debug("Executing measurement query.")
        cursor.execute("""
            SELECT
                measurement_id,
                asset_id,
                measurement_time,
                load_value,
                unit,
                source,
                quality_status
            FROM measurements
            WHERE measurement_id = %s;
        """, (measurement_id,))

        row = cursor.fetchone()

        if row is None:
            return None
        
        return map_detailed_measurement_row(row)

# ============================================================
# Asset Mapping
# ============================================================
def map_asset_row(row):

    asset_id, asset_name, asset_type, asset_location = row

    asset = {"asset_id": asset_id, "asset_name": asset_name, "asset_type": asset_type, "asset_location": asset_location}

    return asset

# ============================================================
# Measurement Mapping
# ============================================================
def map_measurement_row(row):

    asset_name, measurement_time, load_value, unit = row

    measurement = {"asset_name": asset_name, "measurement_time": measurement_time, "load_value": load_value, "unit": unit}

    return measurement

# ============================================================
# Detailed Measurement Mapping
# ============================================================
def map_detailed_measurement_row(row):

    return {        
        "measurement_id": row[0],
        "asset_id": row[1],
        "measurement_time": row[2],
        "load_value": float(row[3]),
        "unit": row[4],
        "source": row[5],
        "quality_status": row[6],
    }

# ============================================================
# Database Report Data Loader
# ============================================================

def fetch_database_report_data():
    conn = get_connection() 

    logger.info("Loading database report data started.")

    try:
        asset_data = fetch_assets(conn) 
        logger.info(f"Loaded {len(asset_data)} assets from database.")
        measurement_data = fetch_joined_measurements(conn) 
        logger.info(f"Loaded {len(measurement_data)} joined measurements from database.")

    finally:
        conn.close() 
        logger.info("Database connection closed.")

    return asset_data, measurement_data

# ============================================================
# Database Create Measurement
# ============================================================

def create_measurement(conn, measurement_data):

    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO measurements (
                asset_id,
                measurement_time,
                load_value,
                unit,
                source,
                quality_status
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING
                measurement_id,
                asset_id,
                measurement_time,
                load_value,
                unit,
                source,
                quality_status;
        """, (
            measurement_data.asset_id,
            measurement_data.measurement_time,
            measurement_data.load_value,
            measurement_data.unit,
            measurement_data.source,
            measurement_data.quality_status,
        ))
    
        row = cursor.fetchone()

    conn.commit()

    return map_detailed_measurement_row(row)

# ============================================================
# Database Patch Measurement
# ============================================================

def update_measurement_quality_status(conn, measurement_id, quality_status):

    with conn.cursor() as cursor:
        cursor.execute("""
            UPDATE measurements
            SET quality_status = %s
            WHERE measurement_id = %s
            RETURNING 
                measurement_id, 
                asset_id, 
                measurement_time, 
                load_value, 
                unit, 
                source, 
                quality_status;     
        """, (
            quality_status,
            measurement_id,
        ))

        row = cursor.fetchone()
    
    conn.commit()

    return map_detailed_measurement_row(row)

# ============================================================
# KPI Measurement Mapping
# ============================================================
def map_kpi_measurement_row(row):

    return {        
        "measurement_count": row[0],
        "average_load": float(row[1]) if row[1] is not None else None,
        "min_load": float(row[2]) if row[2] is not None else None,
        "max_load": float(row[3]) if row[3] is not None else None,
        "latest_measurement_time": row[4],
    }

def map_kpi_measurement_by_asset_id_row(row):

    return {        
        "asset_id": row[0],
        "asset_name": row[1],
        "measurement_count": row[2],
        "average_load": float(row[3]) if row[3] is not None else None,
        "min_load": float(row[4]) if row[4] is not None else None,
        "max_load": float(row[5]) if row[5] is not None else None,
        "latest_measurement_time": row[6],
    }

# ============================================================
# Database Read KPIs
# ============================================================
def fetch_measurement_kpi_summary(conn):

    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT
                COUNT(*) AS measurement_count,
                ROUND(AVG(load_value), 2) AS average_load,
                MIN(load_value) AS min_load,
                MAX(load_value) AS max_load,
                MAX(measurement_time) AS latest_measurement_time
            FROM measurements
            WHERE quality_status = 'valid';
        """)

        row = cursor.fetchone()

    if row is None:
        return None  
    
    return map_kpi_measurement_row(row)

def fetch_asset_kpi_summary(conn, asset_id):

    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT
                COUNT(*) AS measurement_count,
                ROUND(AVG(load_value), 2) AS average_load,
                MIN(load_value) AS min_load,
                MAX(load_value) AS max_load,
                MAX(measurement_time) AS latest_measurement_time
            FROM measurements
            WHERE asset_id = %s
            AND quality_status = 'valid';
        """, (asset_id,))

        row = cursor.fetchone()

    if row is None:
        return None     

    return map_kpi_measurement_row(row)

    