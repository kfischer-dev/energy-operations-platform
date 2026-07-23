import pytest

from src.simulation.models import SimulationAsset
from src.simulation.registry import SIMULATION_PROFILE_REGISTRY
from src.simulation.service import load_simulation_assets


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
