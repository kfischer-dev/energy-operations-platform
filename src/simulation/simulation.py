from datetime import datetime, time
from random import Random

from src.simulation.default_data import (
    create_default_biomass_asset,
    create_default_biomass_context,
    create_default_hydro_plant_asset,
    create_default_hydro_plant_context,
    create_default_simulation_config,
    create_default_solar_asset,
    create_default_solar_context,
    create_default_wind_park_asset,
    create_default_wind_park_context,
)
from src.simulation.engine import simulate_power_of_asset
from src.simulation.models import (
    SimulationAsset,
    SimulationConfig,
    SimulationContext,
    SimulationPowerMeasurementDraft,
)
from src.simulation.profiles import time_to_minutes
from src.simulation.time_grid import generate_time_grid


def create_default_asset(asset_type: str) -> SimulationAsset:
    """Create the default simulation asset for the requested asset type."""

    if asset_type == "solar_park":
        return create_default_solar_asset()

    if asset_type == "wind_park":
        return create_default_wind_park_asset()

    if asset_type == "hydro_power_plant":
        return create_default_hydro_plant_asset()

    if asset_type == "biomass_power_plant":
        return create_default_biomass_asset()

    raise ValueError(
        f"Asset type '{asset_type}' not available for simulation."
    )


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

    raise ValueError(
        f"Asset type '{asset.asset_type}' not available for simulation."
    )


def create_simulation_context(
    config: SimulationConfig,
    asset: SimulationAsset,
    timestamp: datetime,
    random_generator: Random,
) -> SimulationContext:
    """Create the technology-specific context for one timestamp."""

    if asset.asset_type == "solar_park":
        return create_default_solar_context(
            config=config,
            current_time=timestamp,
            random_generator=random_generator,
        )

    if asset.asset_type == "wind_park":
        return create_default_wind_park_context(
            config=config,
            current_time=timestamp,
            random_generator=random_generator,
        )

    if asset.asset_type == "hydro_power_plant":
        return create_default_hydro_plant_context(
            config=config,
            current_time=timestamp,
            random_generator=random_generator,
        )

    if asset.asset_type == "biomass_power_plant":
        return create_default_biomass_context(
            config=config,
            current_time=timestamp,
            random_generator=random_generator,
        )

    raise ValueError(
        f"Asset type '{asset.asset_type}' not available for simulation."
    )


def simulate_asset_power_grid(
    config: SimulationConfig,
    asset: SimulationAsset,
) -> list[SimulationPowerMeasurementDraft]:
    """Simulate active power for every timestamp in the configured grid."""

    random_generator = Random(config.random_seed)
    simulation_time_grid = generate_time_grid(
        config.start_time,
        config.end_time,
        config.interval_minutes,
    )
    profile_data = build_profile_data(asset)

    measurements: list[SimulationPowerMeasurementDraft] = []

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
            SimulationPowerMeasurementDraft(
                asset_id=asset.asset_id,
                measurement_time=context.current_time,
                active_power_kw=active_power_kw,
            )
        )

    return measurements


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
