from src.simulation.models import SimulationAsset
from src.database import get_connection
from src.simulation.repository import fetch_simulation_assets

def map_asset_to_simulation_asset(asset: dict) -> SimulationAsset:
    """Convert a database asset dictionary into a simulation asset."""

    return SimulationAsset(
        asset_id=asset["asset_id"],
        asset_code=asset["asset_code"],
        asset_role=asset["asset_role"],
        asset_type=asset["asset_type"],
        region_id=asset["region_id"],
        region_code=asset["region_code"],
        rated_power_kw=float(asset["rated_power_kw"]),
        operating_status=asset["operating_status"],
        is_renewable=asset["is_renewable"],
        is_weather_dependent=asset["is_weather_dependent"],
        is_dispatchable=asset["is_dispatchable"],
        can_store_energy=asset["can_store_energy"],
    )



def test_mapping():
    conn = get_connection()

    try:
        assets = fetch_simulation_assets(conn)
        print(assets[0])
    finally:
        conn.close()

if __name__ == "__main__":
    test_mapping()