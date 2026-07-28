import logging

from src.measurements.measurement_aggregation import aggregate_measurements_for_intervals
from src.measurements.models import PowerIntervalDraft, PowerMeasurement
from src.simulation.engine import simulate_assets_power_grid
from src.simulation.mapper import map_asset_to_simulation_asset
from src.simulation.models import SimulationAsset, SimulationConfig
from src.simulation.registry import SIMULATION_PROFILE_REGISTRY
from src.simulation.repository import (
    create_simulation_run,
    fetch_simulation_assets,
    insert_power_measurements,
    mark_simulation_run_completed,
    mark_simulation_run_failed,
    mark_simulation_run_running,
)
from src.simulation.simulation import validate_simulation_intervals

logger = logging.getLogger(__name__)


def load_simulation_assets(conn) -> list[SimulationAsset]:
    """Load all simulation assets from the database."""
    supported_asset_types = list(SIMULATION_PROFILE_REGISTRY)

    database_assets = fetch_simulation_assets(conn, supported_asset_types)

    return [map_asset_to_simulation_asset(asset) for asset in database_assets]


def simulate_database_assets(
    conn,
    config: SimulationConfig,
) -> list[PowerMeasurement]:
    """Load database assets and simulate point-in-time power measurements."""

    assets = load_simulation_assets(conn)

    return simulate_assets_power_grid(
        config=config,
        assets=assets,
    )


def aggregate_simulation_measurements(
    measurements: list[PowerMeasurement],
    config: SimulationConfig,
) -> list[PowerIntervalDraft]:
    """Aggregate simulated point measurements for API or frontend output."""

    intervals: list[PowerIntervalDraft] = []
    asset_ids = sorted({measurement.asset_id for measurement in measurements})

    for asset_id in asset_ids:
        asset_measurements = [
            measurement
            for measurement in measurements
            if measurement.asset_id == asset_id
        ]
        intervals.extend(
            aggregate_measurements_for_intervals(
                asset_id=asset_id,
                measurements=asset_measurements,
                start_time=config.start_time,
                end_time=config.effective_end_time,
                interval_minutes=config.interval_minutes,
            )
        )

    return intervals


def execute_simulation_run(conn, config: SimulationConfig) -> list[PowerIntervalDraft]:
    """Run the simulation and return the generated power intervals."""

    simulation_run_id = create_simulation_run(conn, config)
    conn.commit()  # Commit the creation of the simulation run before starting the simulation

    try:
        # Mark the simulation run as running
        mark_simulation_run_running(conn, simulation_run_id)

        conn.commit()  # Commit the status update before starting the simulation

        # Simulate and persist point-in-time power measurements.
        power_measurements = simulate_database_assets(conn, config)
        generated_measurement_count = insert_power_measurements(
            conn,
            power_measurements,
            simulation_run_id,
        )

        # Aggregate only for the current response; intervals are not persisted.
        power_intervals = aggregate_simulation_measurements(
            power_measurements,
            config,
        )
        validate_simulation_intervals(power_intervals)

        # Mark the simulation run as completed.
        mark_simulation_run_completed(
            conn,
            simulation_run_id,
            generated_measurement_count=generated_measurement_count,
        )

        conn.commit()  # Commit the status update and any other changes made during the simulation

        return power_intervals

    except Exception:
        conn.rollback()  # Rollback any changes made during the simulation in case of an error

        # If an error occurs, mark the simulation run as failed
        mark_simulation_run_failed(conn, simulation_run_id)
        logger.exception(
            "Simulation run %s failed.",
            simulation_run_id,
        )

        conn.commit()  # Commit the status update for the failed simulation run

        raise
