from src.measurements.measurement_aggregation import aggregate_measurements_for_intervals
from src.measurements.models import PowerIntervalDraft
from src.simulation.models import (
    SimulationAsset,
    SimulationConfig,
)
from src.simulation.simulation import simulate_asset_power_grid


def simulate_asset_intervals(
    config: SimulationConfig,
    asset: SimulationAsset,
) -> list[PowerIntervalDraft]:
    """Simulate power measurements and aggregate them into intervals."""

    measurements = simulate_asset_power_grid(
        config=config,
        asset=asset,
    )

    return aggregate_measurements_for_intervals(
        asset_id=asset.asset_id,
        measurements=measurements,
        start_time=config.start_time,
        end_time=config.effective_end_time,
        interval_minutes=config.interval_minutes,
    )

def simulate_assets_intervals(
    config: SimulationConfig,
    assets: list[SimulationAsset],
) -> list[PowerIntervalDraft]:
    """Simulate power measurements for multiple assets and aggregate them into intervals."""

    intervals: list[PowerIntervalDraft] = []

    for asset in assets:
        intervals.extend(
            simulate_asset_intervals(
                config=config,
                asset=asset,
            )
        )

    return intervals
