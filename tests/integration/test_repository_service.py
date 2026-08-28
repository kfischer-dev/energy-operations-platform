from datetime import datetime

import psycopg
import pytest

from src.database import (
    fetch_measurement_kpi_summary,
    fetch_measurements_for_asset_kpi_period,
)
from src.measurements.measurement_aggregation import (
    aggregate_measurements_for_intervals,
)
from src.measurements.service import calculate_kpis_for_all_measurements
from src.simulation.default_data import create_default_simulation_config
from src.simulation.models import SimulationAsset
from src.simulation.registry import SIMULATION_PROFILE_REGISTRY
from src.simulation.repository import fetch_simulation_run_by_id
from src.simulation.service import execute_simulation_run, load_simulation_assets
from tests.factories import create_power_measurement


@pytest.mark.integration
def test_load_simulation_assets_returns_supported_database_assets(
    reset_db,
    database_connection,
):
    """Load and map only database assets supported by the simulation registry."""

    assets = load_simulation_assets(database_connection)

    supported_asset_types = set(SIMULATION_PROFILE_REGISTRY)
    loaded_asset_types = {asset.asset_type for asset in assets}

    assert assets
    assert all(isinstance(asset, SimulationAsset) for asset in assets)
    assert loaded_asset_types <= supported_asset_types
    assert "battery_storage" not in loaded_asset_types

    solar_asset = next(asset for asset in assets if asset.asset_code == "E-SOLAR-001")

    assert solar_asset.asset_type == "solar_park"
    assert solar_asset.asset_role == "producer"
    assert solar_asset.region_code == "DE-EAST"
    assert isinstance(solar_asset.rated_power_kw, float)


@pytest.mark.smoke
@pytest.mark.integration
def test_execute_simulation_run_and_save_measurements(
    reset_db,
    client,
    database_connection,
):
    """Run a simulation and save the generated measurements to the database."""

    conn = database_connection
    config = create_default_simulation_config()

    execute_simulation_run(conn, config)

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT simulation_run_id
            FROM simulation_runs
            ORDER BY simulation_run_id DESC
            LIMIT 1;
            """
        )
        simulation_run_id = cursor.fetchone()[0]

    simulation_run = fetch_simulation_run_by_id(conn, simulation_run_id)

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM measurements
            WHERE simulation_run_id = %s;
            """,
            (simulation_run_id,),
        )
        persisted_count = cursor.fetchone()[0]

    assert simulation_run["generated_measurement_count"] == persisted_count
    assert simulation_run["status"] == "completed"

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT measurement_id
            FROM measurements
            WHERE simulation_run_id = %s
            ORDER BY measurement_id
            LIMIT 1;
            """,
            (simulation_run_id,),
        )
        measurement_id = cursor.fetchone()[0]

    response_get = client.get(f"/measurements/{measurement_id}")

    assert response_get.status_code == 200

    data_get = response_get.json()

    assert data_get["measurement_id"] == measurement_id
    assert data_get["source"] == "simulation"
    assert "interval_minutes" not in data_get
    assert "energy_kwh" not in data_get
    assert data_get["active_power_kw"] is not None
    assert data_get["quality_status"] == "valid"


@pytest.mark.failure
@pytest.mark.integration
def test_failure_rollback_simulation_run(
    reset_db,
    client,
    database_connection,
):
    """Simulate a failure during a simulation run and verify rollback."""

    conn = database_connection
    config = create_default_simulation_config()

    execute_simulation_run(conn, config)

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT simulation_run_id
            FROM simulation_runs
            ORDER BY simulation_run_id DESC
            LIMIT 1;
            """
        )
        simulation_run_a_id = cursor.fetchone()[0]

    simulation_run_a = fetch_simulation_run_by_id(conn, simulation_run_a_id)

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM measurements
            WHERE simulation_run_id = %s;
            """,
            (simulation_run_a_id,),
        )
        persisted_count_a = cursor.fetchone()[0]

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM measurements
            """,
        )
        total_measurements_before = cursor.fetchone()[0]

    with pytest.raises(psycopg.errors.UniqueViolation):
        execute_simulation_run(conn, config)

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT simulation_run_id
            FROM simulation_runs
            ORDER BY simulation_run_id DESC
            LIMIT 1;
            """
        )
        simulation_run_b_id = cursor.fetchone()[0]

    simulation_run_b = fetch_simulation_run_by_id(conn, simulation_run_b_id)

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM measurements
            """,
        )
        total_measurements_after = cursor.fetchone()[0]

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM measurements
            WHERE simulation_run_id = %s;
            """,
            (simulation_run_b_id,),
        )
        persisted_count_b = cursor.fetchone()[0]

    assert simulation_run_a["generated_measurement_count"] == persisted_count_a
    assert simulation_run_a["status"] == "completed"
    assert simulation_run_a["generated_measurement_count"] > 0

    assert simulation_run_b["status"] == "failed"
    assert persisted_count_b == 0
    assert simulation_run_b["generated_measurement_count"] == 0

    assert total_measurements_after == total_measurements_before


@pytest.mark.integration
def test_fetch_measurements_for_asset_kpi_period_returns_interval_and_support_points(
    reset_db,
    database_connection,
):

    start_time = datetime.fromisoformat("2026-06-22T08:00:00+02:00")
    end_time = datetime.fromisoformat("2026-06-22T08:30:00+02:00")

    left_support_time = datetime.fromisoformat("2026-06-22T07:45:00+02:00")
    right_support_time = datetime.fromisoformat("2026-06-22T08:45:00+02:00")

    measurements = fetch_measurements_for_asset_kpi_period(
        database_connection,
        asset_id=1,
        start_time=start_time,
        end_time=end_time,
    )

    assert len(measurements) == 5

    assert measurements[0]["measurement_time"] == left_support_time
    assert measurements[-1]["measurement_time"] == right_support_time

    assert all(measurement["asset_id"] == 1 for measurement in measurements)

    measurement_times = [
        measurement["measurement_time"] for measurement in measurements
    ]

    assert measurement_times == sorted(measurement_times)


# ============================================================
# KPI Aggregation
# ============================================================


@pytest.mark.integration
def test_aggregates_measurements_for_asset_kpi(
    reset_db,
    database_connection,
):
    """Aggregates measurements into intervals for a KPI period."""

    # interval_start = datetime(2026, 6, 22, 8, 0)
    # interval_end = datetime(2026, 6, 22, 8, 30)

    start_time = datetime.fromisoformat("2026-06-22T08:00:00+02:00")
    end_time = datetime.fromisoformat("2026-06-22T08:30:00+02:00")

    measurements = fetch_measurements_for_asset_kpi_period(
        database_connection,
        asset_id=1,
        start_time=start_time,
        end_time=end_time,
    )

    power_measurements = [
        create_power_measurement(
            measurement["measurement_time"],
            measurement["active_power_kw"],
            asset_id=measurement["asset_id"],
            source=measurement["source"],
            quality_status=measurement["quality_status"],
        )
        for measurement in measurements
    ]

    intervals = aggregate_measurements_for_intervals(
        asset_id=1,
        measurements=power_measurements,
        start_time=start_time,
        end_time=end_time,
        interval_minutes=15,
    )

    total_energy_kwh = sum(
        interval.energy_kwh for interval in intervals if interval.energy_kwh is not None
    )

    assert len(intervals) == 2

    assert intervals[0].interval_start == start_time
    assert intervals[-1].interval_end == end_time

    assert all(interval.asset_id == 1 for interval in intervals)
    assert all(interval.coverage_ratio == 1.0 for interval in intervals)
    assert all(interval.quality_status == "valid" for interval in intervals)

    assert all(interval.energy_kwh is not None for interval in intervals)
    assert all(interval.avg_active_power_kw is not None for interval in intervals)

    assert total_energy_kwh == pytest.approx(40799.48, abs=0.01)


@pytest.mark.integration
def test_kpi_summary_for_all_measurements(
    reset_db,
    database_connection,
):
    """Calculate global KPI summary for all assets within a period."""

    start_time = datetime.fromisoformat("2026-06-22T08:00:00+02:00")
    end_time = datetime.fromisoformat("2026-06-22T08:30:00+02:00")

    measurements = fetch_measurement_kpi_summary(database_connection)

    kpi_summary = calculate_kpis_for_all_measurements(
        measurements=measurements,
        start_time=start_time,
        end_time=end_time,
    )

    period_measurements = [
        measurement
        for measurement in measurements
        if start_time <= measurement["measurement_time"] <= end_time
    ]

    expected_min_power_kw = min(
        measurement["active_power_kw"] for measurement in period_measurements
    )

    expected_max_power_kw = max(
        measurement["active_power_kw"] for measurement in period_measurements
    )

    # Period contract
    assert kpi_summary["period_start"] == start_time
    assert kpi_summary["period_end"] == end_time

    # Measurement-based KPIs
    assert kpi_summary["measurement_count"] == 21

    assert kpi_summary["min_measured_power_kw"] == pytest.approx(8000.0)
    assert kpi_summary["max_measured_power_kw"] == pytest.approx(149000.0)

    assert kpi_summary["min_measured_power_kw"] == expected_min_power_kw
    assert kpi_summary["max_measured_power_kw"] == expected_max_power_kw

    assert kpi_summary["min_measured_power_kw"] <= kpi_summary["max_measured_power_kw"]

    # Period-based KPIs
    assert kpi_summary["avg_active_power_kw"] == pytest.approx(
        445848.96,
        abs=0.01,
    )
    assert kpi_summary["total_energy_kwh"] == pytest.approx(
        222924.48,
        abs=0.01,
    )

    assert kpi_summary["avg_active_power_kw"] > 0
    assert kpi_summary["total_energy_kwh"] > 0

    # Coverage
    assert kpi_summary["coverage_ratio"] == pytest.approx(0.875)
    assert 0.0 <= kpi_summary["coverage_ratio"] <= 1.0
