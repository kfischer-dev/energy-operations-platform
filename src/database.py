import logging
import os

import psycopg
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# ============================================================
# PostgreSQL Connection Management
# ============================================================


def get_connection():
    """Load database configuration and open a PostgreSQL connection."""

    load_dotenv()

    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")

    logger.info("Connecting to PostgreSQL database...")

    conn = psycopg.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port,
    )
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
                m.measurement_id,
                a.asset_id,
                a.asset_code,
                a.asset_name,
                at.asset_type_name,
                at.asset_role,
                r.region_code,
                m.measurement_time,
                m.active_power_kw,
                m.source,
                m.quality_status
            FROM measurements m
            JOIN assets a
                ON m.asset_id = a.asset_id
            JOIN asset_types at
                ON at.asset_type_id = a.asset_type_id
            JOIN regions r
                ON r.region_id = a.region_id
            ORDER BY a.asset_name, m.measurement_time;
        """)
        rows = cursor.fetchall()

    return [map_measurement_row(row) for row in rows]


def fetch_assets(conn):
    """Return all assets from the database as dictionaries."""

    with conn.cursor() as cursor:
        logger.debug("Executing asset query.")
        cursor.execute("""
            SELECT
                a.asset_id,
                a.asset_name,
                a.asset_code,
                a.asset_location,
                at.asset_role,
                at.asset_type_name,
                r.region_id,
                r.region_code,
                r.region_name,
                a.rated_power_kw,
                a.latitude,
                a.longitude,
                a.operating_status
            FROM assets AS a
            JOIN asset_types AS at
                ON at.asset_type_id = a.asset_type_id
            JOIN regions AS r
                ON r.region_id = a.region_id
            ORDER BY a.asset_id;
        """)
        rows = cursor.fetchall()

    return [map_asset_row(row) for row in rows]


def fetch_asset_summaries(conn):
    """Return compact asset data as dictionaries."""

    with conn.cursor() as cursor:
        logger.debug("Executing asset summary query.")
        cursor.execute("""
            SELECT
                a.asset_id,
                a.asset_name,
                a.asset_code,
                a.asset_location,
                at.asset_role,
                at.asset_type_name,
                r.region_code,
                a.rated_power_kw,
                a.operating_status
            FROM assets AS a
            JOIN asset_types AS at
                ON at.asset_type_id = a.asset_type_id
            JOIN regions AS r
                ON r.region_id = a.region_id
            ORDER BY a.asset_id;
        """)
        rows = cursor.fetchall()

    return [map_asset_summary_row(row) for row in rows]


def fetch_measurements_by_asset_id(conn, asset_id):
    """Return all measurements for a specific asset as dictionaries."""

    with conn.cursor() as cursor:
        logger.debug("Executing joined measurements by asset_id query.")

        # Parameterization keeps SQL execution safe.
        cursor.execute(
            """
            SELECT
                m.measurement_id,
                a.asset_id,
                a.asset_code,
                a.asset_name,
                at.asset_type_name,
                at.asset_role,
                r.region_code,
                m.measurement_time,
                m.active_power_kw,
                m.source,
                m.quality_status
            FROM measurements m
            JOIN assets a
                ON m.asset_id = a.asset_id
            JOIN asset_types at
                ON a.asset_type_id = at.asset_type_id
            JOIN regions r
                ON a.region_id = r.region_id
            WHERE a.asset_id = %s
            ORDER BY a.asset_name, m.measurement_time;
        """,
            (asset_id,),
        )
        rows = cursor.fetchall()

    return [map_measurement_row(row) for row in rows]


def fetch_measurement_summaries(conn):
    """Return compact measurement data as dictionaries."""

    with conn.cursor() as cursor:
        logger.debug("Executing measurement summary query.")
        cursor.execute("""
            SELECT
                m.measurement_id,
                a.asset_id,
                a.asset_code,
                a.asset_name,
                m.measurement_time,
                m.active_power_kw,
                m.quality_status
            FROM measurements AS m
            JOIN assets AS a
                ON a.asset_id = m.asset_id
            ORDER BY a.asset_name, m.measurement_time;
        """)
        rows = cursor.fetchall()

    return [map_measurement_summary_row(row) for row in rows]


def fetch_measurement_summaries_by_asset_id(conn, asset_id):
    """Return compact measurement data for a specific asset as dictionaries."""

    with conn.cursor() as cursor:
        logger.debug("Executing measurement summary query by asset_id.")

        # Parameterization keeps SQL execution safe.
        cursor.execute(
            """
            SELECT
                m.measurement_id,
                a.asset_id,
                a.asset_code,
                a.asset_name,
                m.measurement_time,
                m.active_power_kw,
                m.quality_status
            FROM measurements AS m
            JOIN assets AS a
                ON a.asset_id = m.asset_id
            WHERE a.asset_id = %s
            ORDER BY a.asset_name, m.measurement_time;
        """,
            (asset_id,),
        )
        rows = cursor.fetchall()

    return [map_measurement_summary_row(row) for row in rows]


def fetch_asset_by_id(conn, asset_id):
    """Return one asset by ID, or None if the asset does not exist."""

    with conn.cursor() as cursor:
        logger.debug("Executing asset query.")
        cursor.execute(
            """
            SELECT
                a.asset_id,
                a.asset_name,
                a.asset_code,
                a.asset_location,
                at.asset_role,
                at.asset_type_name,
                r.region_id,
                r.region_code,
                r.region_name,
                a.rated_power_kw,
                a.latitude,
                a.longitude,
                a.operating_status
            FROM assets AS a
            JOIN asset_types AS at
                ON at.asset_type_id = a.asset_type_id
            JOIN regions AS r
                ON r.region_id = a.region_id
            WHERE a.asset_id = %s;
        """,
            (asset_id,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return map_asset_row(row)


def fetch_measurement_by_id(conn, measurement_id):
    """Return measurements of a specific measurement id as dictionary."""

    with conn.cursor() as cursor:
        logger.debug("Executing measurement query.")
        cursor.execute(
            """
            SELECT
                m.measurement_id,
                a.asset_id,
                a.asset_code,
                a.asset_name,
                at.asset_type_name,
                at.asset_role,
                r.region_code,
                m.measurement_time,
                m.active_power_kw,
                m.source,
                m.quality_status
            FROM measurements AS m
            JOIN assets AS a
                ON a.asset_id = m.asset_id
            JOIN asset_types AS at
                ON at.asset_type_id = a.asset_type_id
            JOIN regions AS r
                ON r.region_id = a.region_id
            WHERE m.measurement_id = %s;
        """,
            (measurement_id,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return map_measurement_row(row)


# ============================================================
# Asset Mapping
# ============================================================


def map_asset_summary_row(row):
    (
        asset_id,
        asset_name,
        asset_code,
        asset_location,
        asset_role,
        asset_type,
        region_code,
        rated_power_kw,
        operating_status,
    ) = row

    asset = {
        "asset_id": asset_id,
        "asset_name": asset_name,
        "asset_code": asset_code,
        "asset_location": asset_location,
        "asset_role": asset_role,
        "asset_type": asset_type,
        "region_code": region_code,
        "rated_power_kw": rated_power_kw,
        "operating_status": operating_status,
    }

    return asset


def map_asset_row(row):
    (
        asset_id,
        asset_name,
        asset_code,
        asset_location,
        asset_role,
        asset_type,
        region_id,
        region_code,
        region_name,
        rated_power_kw,
        latitude,
        longitude,
        operating_status,
    ) = row

    asset = {
        "asset_id": asset_id,
        "asset_name": asset_name,
        "asset_code": asset_code,
        "asset_location": asset_location,
        "asset_role": asset_role,
        "asset_type": asset_type,
        "region_id": region_id,
        "region_code": region_code,
        "region_name": region_name,
        "rated_power_kw": rated_power_kw,
        "latitude": latitude,
        "longitude": longitude,
        "operating_status": operating_status,
    }

    return asset


# ============================================================
# Measurement Mapping
# ============================================================


def map_measurement_summary_row(row):
    (
        measurement_id,
        asset_id,
        asset_code,
        asset_name,
        measurement_time,
        active_power_kw,
        quality_status,
    ) = row

    measurement = {
        "measurement_id": measurement_id,
        "asset_id": asset_id,
        "asset_code": asset_code,
        "asset_name": asset_name,
        "measurement_time": measurement_time,
        "active_power_kw": active_power_kw,
        "quality_status": quality_status,
    }

    return measurement


def map_measurement_row(row):
    (
        measurement_id,
        asset_id,
        asset_code,
        asset_name,
        asset_type,
        asset_role,
        region_code,
        measurement_time,
        active_power_kw,
        source,
        quality_status,
    ) = row

    measurement = {
        "measurement_id": measurement_id,
        "asset_id": asset_id,
        "asset_code": asset_code,
        "asset_name": asset_name,
        "asset_type": asset_type,
        "asset_role": asset_role,
        "region_code": region_code,
        "measurement_time": measurement_time,
        "active_power_kw": active_power_kw,
        "source": source,
        "quality_status": quality_status,
    }

    return measurement


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
        logger.info(
            f"Loaded {len(measurement_data)} joined measurements from database."
        )

    finally:
        conn.close()
        logger.info("Database connection closed.")

    return asset_data, measurement_data


# ============================================================
# Database Create Measurement
# ============================================================


def create_measurement(conn, measurement_data):

    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO measurements (
                asset_id,
                measurement_time,
                active_power_kw,
                source,
                quality_status
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING
                measurement_id;
        """,
            (
                measurement_data.asset_id,
                measurement_data.measurement_time,
                measurement_data.active_power_kw,
                measurement_data.source,
                measurement_data.quality_status,
            ),
        )

        measurement_id = cursor.fetchone()[0]

    conn.commit()

    return measurement_id


# ============================================================
# Database Patch Measurement
# ============================================================


def update_measurement_quality_status(conn, measurement_id, quality_status):

    with conn.cursor() as cursor:
        cursor.execute(
            """
            UPDATE measurements
            SET quality_status = %s
            WHERE measurement_id = %s
            RETURNING 
                measurement_id;   
        """,
            (
                quality_status,
                measurement_id,
            ),
        )

        measurement_id = cursor.fetchone()[0]

    conn.commit()

    return measurement_id


# ============================================================
# KPI Measurement Mapping
# ============================================================


def map_kpi_measurement_row(row):

    return {
        "measurement_count": row[0],
        "average_power_kw": float(row[1]) if row[1] is not None else None,
        "min_power_kw": float(row[2]) if row[2] is not None else None,
        "max_power_kw": float(row[3]) if row[3] is not None else None,
        "total_energy_kwh": float(row[4]) if row[4] is not None else None,
        "latest_measurement_time": row[5] if row[5] is not None else None,
    }


# ============================================================
# Database Read KPIs
# ============================================================


def fetch_measurement_kpi_summary(conn):

    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT
                COUNT(*) AS measurement_count,
                ROUND(AVG(active_power_kw), 2) AS average_power_kw,
                MIN(active_power_kw) AS min_power_kw,
                MAX(active_power_kw) AS max_power_kw,
                SUM(energy_kwh) AS total_energy_kwh,
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
        cursor.execute(
            """
            SELECT
                COUNT(*) AS measurement_count,
                ROUND(AVG(active_power_kw), 2) AS average_power_kw,
                MIN(active_power_kw) AS min_power_kw,
                MAX(active_power_kw) AS max_power_kw,
                SUM(energy_kwh) AS total_energy_kwh,
                MAX(measurement_time) AS latest_measurement_time
            FROM measurements
            WHERE asset_id = %s
            AND quality_status = 'valid';
        """,
            (asset_id,),
        )

        row = cursor.fetchone()

    return map_kpi_measurement_row(row)
