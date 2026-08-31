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
        return (time_minutes - sunrise_minutes) / (peak_minutes - sunrise_minutes)

    if peak_minutes <= time_minutes <= sunset_minutes:
        return (sunset_minutes - time_minutes) / (sunset_minutes - peak_minutes)

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


# ============================================================
# Consumer Profiles
# ============================================================

CITY_LOAD_PROFILE = (
    (0, 0.30),
    (5, 0.28),
    (7, 0.55),
    (9, 0.75),
    (12, 0.65),
    (17, 0.70),
    (20, 0.90),
    (23, 0.45),
    (24, 0.30),
)


INDUSTRIAL_LOAD_PROFILE = (
    (0, 0.25),
    (5, 0.25),
    (6, 0.40),
    (8, 0.85),
    (12, 0.90),
    (16, 0.88),
    (18, 0.45),
    (22, 0.28),
    (24, 0.25),
)


def calculate_load_factor(
    profile: tuple[tuple[int, float], ...],
    time_minutes: int,
) -> float:
    """Interpolate the load factor for a given time of day."""

    for i in range(len(profile) - 1):
        start_time, start_load = profile[i]
        end_time, end_load = profile[i + 1]

        start_minutes = start_time * 60
        end_minutes = end_time * 60

        if start_minutes <= time_minutes <= end_minutes:
            return start_load + (
                (end_load - start_load)
                * (time_minutes - start_minutes)
                / (end_minutes - start_minutes)
            )

    raise ValueError("time_minutes must be between 0 and 1440")


def calculate_city_load_kw(
    asset: SimulationAsset,
    context: SimulationContext,
    profile_data: dict[str, dict[str, int]],
) -> float:
    """Simulate city load for one timestamp."""

    time_minutes = context.current_time.hour * 60 + context.current_time.minute

    factor = calculate_load_factor(
        CITY_LOAD_PROFILE,
        time_minutes,
    )

    return asset.rated_power_kw * factor * context.load_factor


def calculate_industrial_load_kw(
    asset: SimulationAsset,
    context: SimulationContext,
    profile_data: dict[str, dict[str, int]],
) -> float:
    """Simulate industrial load for one timestamp."""

    time_minutes = context.current_time.hour * 60 + context.current_time.minute

    factor = calculate_load_factor(
        INDUSTRIAL_LOAD_PROFILE,
        time_minutes,
    )

    return asset.rated_power_kw * factor * context.load_factor
