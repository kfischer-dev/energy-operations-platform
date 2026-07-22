from datetime import time

from src.simulation.models import SimulationAsset, SimulationContext


# ============================================================
# Profile Utilities
# ============================================================


def time_to_minutes(value: time) -> int:
    """Converts a time value to minutes after midnight."""

    return value.hour * 60 + value.minute


def calculate_daylight_factor(
    time_minutes: int,
    sunrise_minutes: int,
    peak_minutes: int,
    sunset_minutes: int,
) -> float:
    """Calculates a triangular daylight factor between sunrise and sunset."""

    if not sunrise_minutes < peak_minutes < sunset_minutes:
        raise ValueError("Sequence of sun times is wrong!")

    if sunrise_minutes <= time_minutes <= peak_minutes:
        return (time_minutes - sunrise_minutes) / (
            peak_minutes - sunrise_minutes
        )

    if peak_minutes <= time_minutes <= sunset_minutes:
        return (sunset_minutes - time_minutes) / (
            sunset_minutes - peak_minutes
        )

    return 0.0


# ============================================================
# Generation Profiles
# ============================================================


def calculate_solar_power_kw(
    asset: SimulationAsset,
    context: SimulationContext,
    profile_data: dict[str, dict[str, int]],
) -> float:
    """Calculates solar power for one simulation timestamp."""

    asset_profile = profile_data[asset.asset_type]
    daylight_factor = calculate_daylight_factor(
        time_minutes=time_to_minutes(context.current_time.time()),
        sunrise_minutes=asset_profile["sunrise_minutes"],
        peak_minutes=asset_profile["peak_minutes"],
        sunset_minutes=asset_profile["sunset_minutes"],
    )

    return asset.rated_power_kw * daylight_factor * context.solar_factor


def calculate_wind_power_kw(
    asset: SimulationAsset,
    context: SimulationContext,
    profile_data: dict[str, dict[str, int]],
) -> float:
    """Calculates wind power with seeded random variation."""

    variation = context.random_generator.uniform(-0.15, 0.15)
    final_wind_factor = context.wind_factor + variation

    return asset.rated_power_kw * final_wind_factor


def calculate_hydro_power_kw(
    asset: SimulationAsset,
    context: SimulationContext,
    profile_data: dict[str, dict[str, int]],
) -> float:
    """Calculates hydro power from the configured context factor."""

    return asset.rated_power_kw * context.hydro_factor


def calculate_biomass_power_kw(
    asset: SimulationAsset,
    context: SimulationContext,
    profile_data: dict[str, dict[str, int]],
) -> float:
    """Calculates biomass power from the configured context factor."""

    return asset.rated_power_kw * context.biomass_factor
