from collections import Counter
from datetime import datetime, timedelta
from dataclasses import replace

from src.database import get_connection
from src.simulation.default_data import create_default_simulation_config
from src.simulation.repository import fetch_simulation_run_by_id
from src.simulation.service import execute_simulation_run


def run_simulation_service_smoke_test() -> bool:
    """Run a real simulation and display the persisted measurement results."""

    # WARNING:
    # This script uses the regular database connection and therefore writes
    # simulation runs and measurements to the configured application database.
    # It is intended for manual smoke/demo runs, not for automated test execution.

    config = create_default_simulation_config()

    start_time = datetime.now().astimezone().replace(
        minute=0,
        second=0,
        microsecond=0,
    )

    config = replace(
        config,
        start_time=start_time,
        end_time=start_time + timedelta(hours=6),
    )

    conn = get_connection()

    try:
        power_intervals = execute_simulation_run(conn, config)

        # The smoke script runs synchronously, so the newest run is the one
        # created by execute_simulation_run() above.
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

        # Read the measurements that were actually persisted for this run.
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    m.asset_id,
                    a.asset_code,
                    COUNT(*) AS measurement_count
                FROM measurements AS m
                JOIN assets AS a
                    ON a.asset_id = m.asset_id
                WHERE m.simulation_run_id = %s
                GROUP BY
                    m.asset_id,
                    a.asset_code
                ORDER BY m.asset_id;
                """,
                (simulation_run_id,),
            )
            measurement_rows = cursor.fetchall()

        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM measurements
                WHERE simulation_run_id = %s;
                """,
                (simulation_run_id,),
            )
            persisted_measurement_count = cursor.fetchone()[0]

        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM measurements;
                """
            )
            total_measurement_count = cursor.fetchone()[0]

    finally:
        conn.close()

    interval_count_by_asset = Counter(
        interval.asset_id for interval in power_intervals
    )
    interval_asset_ids = set(interval_count_by_asset)

    measurement_asset_ids = {row[0] for row in measurement_rows}
    expected_intervals_per_asset = config.total_intervals

    missing_interval_asset_ids = measurement_asset_ids - interval_asset_ids
    unexpected_interval_asset_ids = interval_asset_ids - measurement_asset_ids

    assets_with_wrong_interval_count = {
        asset_id: interval_count
        for asset_id, interval_count in interval_count_by_asset.items()
        if interval_count != expected_intervals_per_asset
    }

    run_completed = simulation_run["status"] == "completed"
    measurement_count_matches = (
        simulation_run["generated_measurement_count"]
        == persisted_measurement_count
    )

    passed = (
        run_completed
        and persisted_measurement_count > 0
        and measurement_count_matches
        and bool(power_intervals)
        and not missing_interval_asset_ids
        and not unexpected_interval_asset_ids
        and not assets_with_wrong_interval_count
    )

    print("=" * 72)
    print("SIMULATION SERVICE SMOKE DEMO")
    print("=" * 72)
    print(f"Simulation Run ID:             {simulation_run_id}")
    print(f"Status:                        {simulation_run['status']}")
    print(
        "Generated Measurements:        "
        f"{simulation_run['generated_measurement_count']}"
    )
    print(f"Persisted Measurements:        {persisted_measurement_count}")
    print(f"Total Measurements in DB:      {total_measurement_count}")
    print(f"Generated Power Intervals:     {len(power_intervals)}")
    print(f"Expected Intervals per Asset:  {expected_intervals_per_asset}")
    print("-" * 72)

    if measurement_rows:
        print(
            "Asset-ID | Asset-Code       | Measurements | Intervals"
        )
        print("-" * 72)

        for asset_id, asset_code, measurement_count in measurement_rows:
            interval_count = interval_count_by_asset.get(asset_id, 0)
            print(
                f"{asset_id:>8} | "
                f"{asset_code:<16} | "
                f"{measurement_count:>12} | "
                f"{interval_count:>9}"
            )
    else:
        print("No measurements were persisted for this simulation run.")

    print("-" * 72)

    if missing_interval_asset_ids:
        print(
            "Measurements without intervals for asset IDs: "
            f"{sorted(missing_interval_asset_ids)}"
        )

    if unexpected_interval_asset_ids:
        print(
            "Intervals without persisted measurements for asset IDs: "
            f"{sorted(unexpected_interval_asset_ids)}"
        )

    if assets_with_wrong_interval_count:
        print(
            "Assets with unexpected interval count: "
            f"{assets_with_wrong_interval_count}"
        )

    if not measurement_count_matches:
        print(
            "Persisted measurement count does not match "
            "simulation_runs.generated_measurement_count."
        )

    print(f"Result:                        {'PASSED' if passed else 'FAILED'}")
    print("=" * 72)

    return passed


if __name__ == "__main__":
    raise SystemExit(0 if run_simulation_service_smoke_test() else 1)
