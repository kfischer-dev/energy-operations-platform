from dataclasses import replace
from datetime import datetime, time
from random import Random

from src.measurements.models import PowerIntervalDraft, PowerMeasurement
from src.simulation.default_data import create_default_simulation_config
from src.simulation.models import (
    SimulationAsset,
    SimulationConfig,
    SimulationContext,
)
from src.simulation.profiles import time_to_minutes
from src.simulation.registry import SIMULATION_PROFILE_REGISTRY
from src.simulation.time_grid import generate_time_grid

# ============================================================
# Simulation Setup
# ============================================================


def create_default_asset(asset_type: str) -> SimulationAsset:
    """Create the default simulation asset for the requested asset type."""

    profile_definition = SIMULATION_PROFILE_REGISTRY.get(asset_type)

    if profile_definition is None:
        raise ValueError(f"Asset type '{asset_type}' not available for simulation.")

    return profile_definition.default_asset_factory()


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
        "city_load",
        "industrial_load",
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

    profile_definition = SIMULATION_PROFILE_REGISTRY.get(asset.asset_type)

    if profile_definition is None:
        raise ValueError(
            f"Asset type '{asset.asset_type}' not available for simulation."
        )

    return profile_definition.context_factory(
        config=config,
        current_time=timestamp,
        random_generator=random_generator,
    )


def validate_simulation_intervals(
    power_intervals: list[PowerIntervalDraft],
) -> None:
    """Validate that all simulated interval results are complete."""

    for interval in power_intervals:
        validate_complete_interval(interval)


def validate_complete_interval(power_interval: PowerIntervalDraft) -> None:
    """Validate that one simulated interval result is complete."""

    power = power_interval.avg_active_power_kw
    energy = power_interval.energy_kwh

    if power_interval.quality_status != "valid":
        raise ValueError("Invalid simulation quality status detected.")

    if power is None or power < 0:
        raise ValueError("Invalid average active power value detected.")

    if energy is None or energy < 0:
        raise ValueError("Invalid energy value detected.")

    if power_interval.coverage_ratio != 1.0:
        raise ValueError("Incomplete simulation interval detected.")


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

    profile_definition = SIMULATION_PROFILE_REGISTRY.get(asset.asset_type)

    if profile_definition is None:
        raise NotImplementedError(
            f"Asset type '{asset.asset_type}' is not supported yet."
        )

    final_active_power_kw = profile_definition.power_profile(
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


def run_default_simulation(asset_type: str) -> None:
    """Run and print one default simulation for local manual inspection."""

    config = create_default_simulation_config()

    config = replace(
        config,
        start_time=datetime(2026, 7, 16, 0, 0),
        end_time=datetime(2026, 7, 17, 0, 0),
        interval_minutes=60,
    )

    asset = create_default_asset(asset_type)
    measurements = simulate_asset_power_grid(config, asset)

    print(f"\n--- {asset.asset_code} ({asset.asset_type}) ---")
    print(f"{'Time':<8} {'Power [kW]':>12} {'Load [%]':>10}")
    print("-" * 34)

    for measurement in measurements:
        load_percent = measurement.active_power_kw / asset.rated_power_kw * 100

        print(
            f"{measurement.measurement_time:%H:%M} "
            f"{measurement.active_power_kw:>12.1f} "
            f"{load_percent:>9.1f}%"
        )


if __name__ == "__main__":
    run_default_simulation("solar_park")
    run_default_simulation("wind_park")
    run_default_simulation("hydro_power_plant")
    run_default_simulation("biomass_power_plant")
    run_default_simulation("city_load")
    run_default_simulation("industrial_load")
