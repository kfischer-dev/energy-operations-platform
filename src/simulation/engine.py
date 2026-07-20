from src.simulation.models import SimulationAsset, SimulationContext
from src.simulation.profiles import (
    calculate_solar_power_kw,
    time_to_minutes,
)


def simulate_power_of_asset(
    asset: SimulationAsset,
    context: SimulationContext,
    profile_data: dict[str, dict[str, int]],
) -> float:
    """Calculate active power for one asset at one simulation timestamp."""

    if asset.operating_status != "online":
        return 0.0

    if asset.asset_type == "solar_park":
        asset_profile = profile_data[asset.asset_type]
        active_power_kw = calculate_solar_power_kw(
            rated_power_kw=asset.rated_power_kw,
            time_minutes=time_to_minutes(context.current_time.time()),
            sunrise_minutes=asset_profile["sunrise_minutes"],
            peak_minutes=asset_profile["peak_minutes"],
            sunset_minutes=asset_profile["sunset_minutes"],
        )
        final_active_power_kw = active_power_kw * context.solar_factor

    elif asset.asset_type == "wind_park":
        variation = context.random_generator.uniform(-0.15, 0.15)
        final_wind_factor = context.wind_factor + variation
        final_active_power_kw = asset.rated_power_kw * final_wind_factor

    elif asset.asset_type == "hydro_power_plant":
        final_active_power_kw = (
            asset.rated_power_kw * context.hydro_factor
        )

    elif asset.asset_type == "biomass_power_plant":
        final_active_power_kw = (
            asset.rated_power_kw * context.biomass_factor
        )

    else:
        raise NotImplementedError(
            f"Asset type '{asset.asset_type}' is not supported yet."
        )

    if final_active_power_kw > asset.rated_power_kw:
        raise ValueError(
            f"Active power of {asset.asset_code} exceeds rated power!"
        )

    if final_active_power_kw < 0:
        raise ValueError(
            f"Active power of {asset.asset_code} is negative!"
        )

    return final_active_power_kw
