from datetime import datetime, time
from random import Random

from src.measurements.models import PowerMeasurement
from src.simulation.default_data import create_default_simulation_config
from src.simulation.models import (
    SimulationAsset,
    SimulationConfig,
    SimulationContext,
)
from src.simulation.profiles import time_to_minutes
from src.simulation.registry import (
    DEFAULT_ASSET_REGISTRY,
    DEFAULT_CONTEXT_REGISTRY,
    POWER_PROFILE_REGISTRY,
)
from src.simulation.time_grid import generate_time_grid

# ============================================================
# Simulation Setup
# ============================================================


def create_default_asset(asset_type: str) -> SimulationAsset:
    """Create the default simulation asset for the requested asset type."""

    default_asset_function = DEFAULT_ASSET_REGISTRY.get(asset_type)

    if default_asset_function is None:
        raise ValueError(f"Asset type '{asset_type}' not available for simulation.")

    return default_asset_function()


def build_profile_data(
    asset: SimulationAsset,
) -> dict[str, dict[str, int]]:
    """Build the profile parameters required by the selected asset type."""

    if asset.asset_type == "solar_park":
        sunrise_time = time(6, 30)
        peak_time = time(12, 30)
        sunset_time = time(18, 30)

        return {
            "solar_park": {
                "sunrise_minutes": time_to_minutes(sunrise_time),
                "peak_minutes": time_to_minutes(peak_time),
                "sunset_minutes": time_to_minutes(sunset_time),
            }
        }

    if asset.asset_type in {
        "wind_park",
        "hydro_power_plant",
        "biomass_power_plant",
    }:
        return {asset.asset_type: {}}

    raise ValueError(f"Asset type '{asset.asset_type}' not available for simulation.")


def create_simulation_context(
    config: SimulationConfig,
    asset: SimulationAsset,
    timestamp: datetime,
    random_generator: Random,
) -> SimulationContext:
    """Create the technology-specific context for one timestamp."""

    default_context_function = DEFAULT_CONTEXT_REGISTRY.get(asset.asset_type)

    if default_context_function is None:
        raise ValueError(
            f"Asset type '{asset.asset_type}' not available for simulation."
        )

    return default_context_function(
        config=config,
        current_time=timestamp,
        random_generator=random_generator,
    )


# ============================================================
# Measurement Generation
# ============================================================


def simulate_power_of_asset(
    asset: SimulationAsset,
    context: SimulationContext,
    profile_data: dict[str, dict[str, int]],
) -> float:
    """Calculate active power for one asset at one simulation timestamp."""

    if asset.operating_status != "online":
        return 0.0

    profile_function = POWER_PROFILE_REGISTRY.get(asset.asset_type)

    if profile_function is None:
        raise NotImplementedError(
            f"Asset type '{asset.asset_type}' is not supported yet."
        )

    final_active_power_kw = profile_function(
        asset=asset,
        context=context,
        profile_data=profile_data,
    )

    if final_active_power_kw > asset.rated_power_kw:
        raise ValueError(f"Active power of {asset.asset_code} exceeds rated power!")

    if final_active_power_kw < 0:
        raise ValueError(f"Active power of {asset.asset_code} is negative!")

    return final_active_power_kw


def simulate_asset_power_grid(
    config: SimulationConfig,
    asset: SimulationAsset,
) -> list[PowerMeasurement]:
    """Simulate active power for every timestamp in the configured grid."""

    random_generator = Random(config.random_seed)
    simulation_time_grid = generate_time_grid(
        config.start_time,
        config.end_time,
        config.interval_minutes,
    )
    profile_data = build_profile_data(asset)

    measurements: list[PowerMeasurement] = []

    for timestamp in simulation_time_grid:
        context = create_simulation_context(
            config,
            asset,
            timestamp,
            random_generator,
        )
        active_power_kw = simulate_power_of_asset(
            asset,
            context,
            profile_data,
        )

        measurements.append(
            PowerMeasurement(
                asset_id=asset.asset_id,
                measurement_time=context.current_time,
                active_power_kw=active_power_kw,
                source="simulation",
                quality_status="valid",
            )
        )

    return measurements


# ============================================================
# Manual Execution
# ============================================================


def simulation(asset_type: str) -> None:
    """Run and print one default simulation for local manual inspection."""

    config = create_default_simulation_config()
    asset = create_default_asset(asset_type)
    measurements = simulate_asset_power_grid(config, asset)

    print(measurements)


if __name__ == "__main__":
    simulation("solar_park")
    simulation("wind_park")
    simulation("hydro_power_plant")
    simulation("biomass_power_plant")
