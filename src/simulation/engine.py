from src.simulation.models import SimulationAsset, SimulationContext
from src.simulation.profiles import (
    calculate_solar_power_kw,
    calculate_wind_power_kw,
    calculate_hydro_power_kw,
    calculate_biomass_power_kw
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

        final_active_power_kw = calculate_solar_power_kw(
            asset=asset,
            context=context,
            profile_data=profile_data,
        )

    elif asset.asset_type == "wind_park":

        final_active_power_kw = calculate_wind_power_kw(
            asset=asset,
            context=context,
            profile_data=profile_data,
        )

    elif asset.asset_type == "hydro_power_plant":

        final_active_power_kw = calculate_hydro_power_kw(
            asset=asset,
            context=context,
            profile_data=profile_data,
        )

    elif asset.asset_type == "biomass_power_plant":
        final_active_power_kw = calculate_biomass_power_kw(
            asset=asset,
            context=context,
            profile_data=profile_data,
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
