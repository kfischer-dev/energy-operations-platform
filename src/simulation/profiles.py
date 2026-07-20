from datetime import time
from src.simulation.models import SimulationAsset, SimulationContext

def calculate_daylight_factor(
    time_minutes: int,
    sunrise_minutes: int,
    peak_minutes: int,
    sunset_minutes: int,
) -> float:
    """Calculate a triangular daylight factor between sunrise and sunset."""

    if not sunrise_minutes < peak_minutes < sunset_minutes:
        raise ValueError("Sequence of sun times is wrong!")

    if sunrise_minutes <= time_minutes <= peak_minutes:
        return ( time_minutes - sunrise_minutes ) / ( peak_minutes - sunrise_minutes )

    if peak_minutes <= time_minutes <= sunset_minutes:
        return ( sunset_minutes - time_minutes ) / ( sunset_minutes - peak_minutes )

    return 0.0

def calculate_solar_power_kw(
    asset: SimulationAsset,
    context: SimulationContext,
    profile_data: dict[str, dict[str, int]],
) -> float:
    asset_profile = profile_data[asset.asset_type]

    daylight_factor = calculate_daylight_factor(
        time_minutes=time_to_minutes(context.current_time.time()),
        sunrise_minutes=asset_profile["sunrise_minutes"],
        peak_minutes=asset_profile["peak_minutes"],
        sunset_minutes=asset_profile["sunset_minutes"],
    )

    active_power_kw = asset.rated_power_kw * daylight_factor

    return active_power_kw * context.solar_factor

def calculate_wind_power_kw(
    asset: SimulationAsset,
    context: SimulationContext,
    profile_data: dict[str, dict[str, int]],
) -> float:
    
    variation = context.random_generator.uniform(-0.15, 0.15)
    final_wind_factor = context.wind_factor + variation

    return asset.rated_power_kw * final_wind_factor

def calculate_hydro_power_kw(
    asset: SimulationAsset,
    context: SimulationContext,
    profile_data: dict[str, dict[str, int]],
) -> float:

    return asset.rated_power_kw * context.hydro_factor

def calculate_biomass_power_kw(
    asset: SimulationAsset,
    context: SimulationContext,
    profile_data: dict[str, dict[str, int]],
) -> float:

    return asset.rated_power_kw * context.biomass_factor


def time_to_minutes(value: time) -> int:
    """Convert a time value to minutes after midnight."""

    return value.hour * 60 + value.minute
