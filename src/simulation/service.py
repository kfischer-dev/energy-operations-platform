from src.measurements.models import PowerIntervalDraft
from src.simulation.engine import simulate_assets_intervals
from src.simulation.mapper import map_asset_to_simulation_asset
from src.simulation.models import SimulationAsset, SimulationConfig
from src.simulation.repository import fetch_simulation_assets


def load_simulation_assets(conn) -> list[SimulationAsset]:
    """Load all simulation assets from the database."""
    database_assets = fetch_simulation_assets(conn)

    return [map_asset_to_simulation_asset(asset) for asset in database_assets]


def simulate_database_assets(
    conn,
    config: SimulationConfig,
) -> list[PowerIntervalDraft]:
    """Load database assets and simulate their power intervals."""

    assets = load_simulation_assets(conn)

    return simulate_assets_intervals(
        config=config,
        assets=assets,
    )
