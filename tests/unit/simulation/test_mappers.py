from decimal import Decimal
from unittest.mock import Mock, patch

import pytest

from src.measurements.models import PowerIntervalDraft
from src.simulation.mapper import map_asset_to_simulation_asset
from src.simulation.models import SimulationAsset, SimulationConfig
from src.simulation.registry import SIMULATION_PROFILE_REGISTRY
from src.simulation.repository import map_simulation_asset_row
from src.simulation.service import load_simulation_assets, simulate_database_assets


@pytest.mark.unit
def test_map_database_asset_to_simulation_asset():
    database_row = (
        1,  # asset_id
        "SOLAR-001",  # asset_code
        "producer",  # asset_role
        "solar_park",  # asset_type
        10,  # region_id
        "DE-NORTH",  # region_code
        Decimal("50_000.00"),  # rated_power_kw
        "online",  # operating_status
        True,  # is_renewable
        True,  # is_weather_dependent
        False,  # is_dispatchable
        False,  # can_store_energy
    )

    database_asset = map_simulation_asset_row(database_row)
    result = map_asset_to_simulation_asset(database_asset)

    assert isinstance(result, SimulationAsset)
    assert result.asset_id == 1
    assert result.asset_code == "SOLAR-001"
    assert result.asset_role == "producer"
    assert result.asset_type == "solar_park"
    assert result.region_id == 10
    assert result.region_code == "DE-NORTH"
    assert isinstance(result.rated_power_kw, float)
    assert result.rated_power_kw == 50_000.0
    assert result.operating_status == "online"
    assert result.is_renewable is True
    assert result.is_weather_dependent is True
    assert result.is_dispatchable is False
    assert result.can_store_energy is False


@pytest.mark.unit
def test_load_simulation_assets():
    """Map all repository results to SimulationAsset objects.

    The repository call is mocked to isolate the service from the database.
    This keeps the test deterministic and verifies only the loading and
    mapping behavior of load_simulation_assets().
    """

    connection = Mock()

    database_assets = [
        {
            "asset_id": 1,
            "asset_code": "SOLAR-001",
            "asset_role": "producer",
            "asset_type": "solar_park",
            "region_id": 10,
            "region_code": "DE-NORTH",
            "rated_power_kw": Decimal("50_000.00"),
            "operating_status": "online",
            "is_renewable": True,
            "is_weather_dependent": True,
            "is_dispatchable": False,
            "can_store_energy": False,
        },
        {
            "asset_id": 2,
            "asset_code": "BATTERY-001",
            "asset_role": "storage",
            "asset_type": "battery_storage",
            "region_id": 20,
            "region_code": "DE-SOUTH",
            "rated_power_kw": Decimal("25_000.00"),
            "operating_status": "online",
            "is_renewable": False,
            "is_weather_dependent": False,
            "is_dispatchable": True,
            "can_store_energy": True,
        },
    ]

    with patch(
        "src.simulation.service.fetch_simulation_assets",
        return_value=database_assets,
    ) as fetch_simulation_assets_mock:
        result = load_simulation_assets(connection)

    fetch_simulation_assets_mock.assert_called_once_with(
        connection,
        list(SIMULATION_PROFILE_REGISTRY),
    )
    assert len(result) == 2
    assert all(isinstance(asset, SimulationAsset) for asset in result)
    assert [asset.asset_id for asset in result] == [1, 2]
    assert result[0].rated_power_kw == 50000.0
    assert isinstance(result[0].rated_power_kw, float)
    assert result[1].can_store_energy is True
    assert result[1].is_dispatchable is True


@pytest.mark.unit
def test_simulate_database_assets_runs_simulation_for_loaded_assets():
    """Load simulation assets, pass them to the engine, and return its result.

    Both dependencies are mocked to isolate the orchestration logic from the
    database and the actual simulation. The test verifies that the service
    calls each dependency with the correct arguments and returns the simulation
    result unchanged.
    """
    connection = Mock()
    config = Mock(spec=SimulationConfig)

    # Placeholder assets returned by the mocked loading service.
    loaded_assets = [
        Mock(spec=SimulationAsset),
        Mock(spec=SimulationAsset),
    ]

    # Placeholder result returned by the mocked simulation engine.
    expected_intervals = [
        Mock(spec=PowerIntervalDraft),
        Mock(spec=PowerIntervalDraft),
    ]

    with (
        patch(
            "src.simulation.service.load_simulation_assets",
            return_value=loaded_assets,
        ) as load_simulation_assets_mock,
        patch(
            "src.simulation.service.simulate_assets_intervals",
            return_value=expected_intervals,
        ) as simulate_assets_intervals_mock,
    ):
        result = simulate_database_assets(connection, config)

    load_simulation_assets_mock.assert_called_once_with(connection)
    simulate_assets_intervals_mock.assert_called_once_with(
        config=config,
        assets=loaded_assets,
    )

    assert result is expected_intervals
