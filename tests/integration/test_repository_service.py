import pytest
from src.simulation.default_data import create_default_simulation_config
from src.simulation.models import SimulationAsset
from src.simulation.registry import SIMULATION_PROFILE_REGISTRY
from src.simulation.service import execute_simulation_run, load_simulation_assets
from src.simulation.repository import fetch_simulation_run_by_id


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

    power_intervals = execute_simulation_run(conn, config)

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
    assert data_get["interval_minutes"] is None
    assert data_get["energy_kwh"] is None
    assert data_get["active_power_kw"] is not None
    assert data_get["quality_status"] == "valid"