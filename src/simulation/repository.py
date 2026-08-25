import logging

from src.measurements.models import PowerMeasurement
from src.simulation.mapper import (
    map_simulation_asset_row,
    map_simulation_run_row,
)
from src.simulation.models import SimulationConfig

logger = logging.getLogger(__name__)

# ============================================================
# Simulation Asset Repository
# ============================================================


def fetch_simulation_assets(conn, supported_asset_types: list[str]) -> list[dict]:
    """Return all database assets required by the simulation."""

    with conn.cursor() as cursor:
        logger.debug("Executing simulation asset query.")

        cursor.execute(
            """
            SELECT
                a.asset_id,
                a.asset_code,
                at.asset_role,
                at.asset_type_name,
                r.region_id,
                r.region_code,
                a.rated_power_kw,
                a.operating_status,
                at.is_renewable,
                at.is_weather_dependent,
                at.is_dispatchable,
                at.can_store_energy
            FROM assets AS a
            JOIN asset_types AS at
                ON at.asset_type_id = a.asset_type_id
            JOIN regions AS r
                ON r.region_id = a.region_id
            WHERE at.asset_type_name = ANY(%s)
            ORDER BY a.asset_id;
        """,
            (supported_asset_types,),
        )

        rows = cursor.fetchall()

    return [map_simulation_asset_row(row) for row in rows]


# ============================================================
# Simulation Run Repository
# ============================================================


def create_simulation_run(conn, config: "SimulationConfig") -> int:
    """Create a new simulation run in the database and return its ID."""
    logger.debug("Creating a new simulation run in the database.")

    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO simulation_runs (
                simulation_mode,
                start_time, 
                end_time, 
                interval_minutes, 
                random_seed, 
                status
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING simulation_run_id;
        """,
            (
                config.simulation_mode,
                config.start_time,
                config.end_time,
                config.interval_minutes,
                config.random_seed,
                "created",
            ),
        )

        simulation_run_id = cursor.fetchone()[0]
        logger.info(f"Created new simulation run with ID: {simulation_run_id}")

    return simulation_run_id


def mark_simulation_run_running(conn, simulation_run_id):
    logger.debug(f"Marking simulation run {simulation_run_id} as running.")

    with conn.cursor() as cursor:
        cursor.execute(
            """
            UPDATE simulation_runs
            SET status = %s,
                started_at = CURRENT_TIMESTAMP
            WHERE simulation_run_id = %s;
            """,
            ("running", simulation_run_id),
        )

    logger.info(f"Simulation run {simulation_run_id} marked as running.")


def mark_simulation_run_completed(
    conn, simulation_run_id, generated_measurement_count: int = 0
):
    logger.debug(f"Marking simulation run {simulation_run_id} as completed.")

    with conn.cursor() as cursor:
        cursor.execute(
            """
            UPDATE simulation_runs
            SET status = %s,
                completed_at = CURRENT_TIMESTAMP,
                generated_measurement_count = %s
            WHERE simulation_run_id = %s;
            """,
            ("completed", generated_measurement_count, simulation_run_id),
        )

    logger.info(f"Simulation run {simulation_run_id} marked as completed.")


def mark_simulation_run_failed(conn, simulation_run_id):
    logger.debug(f"Marking simulation run {simulation_run_id} as failed.")

    with conn.cursor() as cursor:
        cursor.execute(
            """
            UPDATE simulation_runs
            SET status = %s,
                completed_at = CURRENT_TIMESTAMP
            WHERE simulation_run_id = %s;
            """,
            ("failed", simulation_run_id),
        )

    logger.info(f"Simulation run {simulation_run_id} marked as failed.")


def fetch_simulation_run_by_id(conn, simulation_run_id) -> dict | None:
    """Fetch a simulation run by its ID."""
    logger.debug(f"Fetching simulation run with ID: {simulation_run_id}")

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                simulation_run_id,
                simulation_mode,
                start_time,
                end_time,
                interval_minutes,
                random_seed,
                status,
                created_at,
                started_at,
                completed_at,
                generated_measurement_count
            FROM simulation_runs
            WHERE simulation_run_id = %s;
        """,
            (simulation_run_id,),
        )

        row = cursor.fetchone()

    if row is None:
        logger.warning(f"No simulation run found with ID: {simulation_run_id}")
        return None

    return map_simulation_run_row(row)


# ============================================================
# Simulation Measurement Repository
# ============================================================

def insert_power_measurements(
    conn,
    measurements: list[PowerMeasurement],
    simulation_run_id: int,
) -> int:
    """Persist simulated point-in-time power measurements."""

    if not measurements:
        return 0

    rows = [
        (
            measurement.asset_id,
            simulation_run_id,
            measurement.measurement_time,
            measurement.active_power_kw,
            measurement.source,
            measurement.quality_status,
        )
        for measurement in measurements
    ]

    with conn.cursor() as cursor:
        cursor.executemany(
            """
            INSERT INTO measurements (
                asset_id,
                simulation_run_id,
                measurement_time,
                active_power_kw,
                source,
                quality_status
            )
            VALUES (%s, %s, %s, %s, %s, %s);
            """,
            rows,
        )

    return len(rows)
