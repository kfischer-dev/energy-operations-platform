from src.simulation.models import SimulationAsset


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
