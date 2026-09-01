from datetime import datetime

import pytest

from src.measurements.models import PowerIntervalDraft
from src.simulation.engine import (
    simulate_asset_intervals,
    simulate_assets_intervals,
)
from src.simulation.models import (
    SimulationAsset,
    SimulationConfig,
)


@pytest.mark.simulation
@pytest.mark.parametrize("engine_payload", ["solar_park"], indirect=True)
def test_simulate_asset_intervals_returns_aggregated_intervals(
    engine_payload,
) -> None:
    """Simulate and aggregate consecutive intervals for one asset."""

    intervals = simulate_asset_intervals(
        config=engine_payload["config"],
        asset=engine_payload["asset"],
    )

    assert len(intervals) == engine_payload["config"].total_intervals
    assert all(isinstance(interval, PowerIntervalDraft) for interval in intervals)
    assert all(
        interval.asset_id == engine_payload["asset"].asset_id for interval in intervals
    )


@pytest.mark.simulation
def test_simulate_assets_intervals_returns_intervals_for_multiple_assets() -> None:
    """Simulate and aggregate intervals for producer and consumer assets."""

    config = SimulationConfig(
        start_time=datetime(2026, 7, 16, 0, 0),
        end_time=datetime(2026, 7, 17, 0, 0),
        interval_minutes=60,
        random_seed=1,
        simulation_mode="historical",
    )

    assets = [
        SimulationAsset(
            asset_id=1,
            asset_code="S-SOLAR-001",
            asset_role="producer",
            asset_type="solar_park",
            region_id=2,
            region_code="DE-SOUTH",
            rated_power_kw=40_000,
            operating_status="online",
            is_renewable=True,
            is_weather_dependent=True,
            is_dispatchable=False,
            can_store_energy=False,
        ),
        SimulationAsset(
            asset_id=2,
            asset_code="N-WIND-001",
            asset_role="producer",
            asset_type="wind_park",
            region_id=1,
            region_code="DE-NORTH",
            rated_power_kw=120_000,
            operating_status="online",
            is_renewable=True,
            is_weather_dependent=True,
            is_dispatchable=False,
            can_store_energy=False,
        ),
        SimulationAsset(
            asset_id=3,
            asset_code="N-CITY-001",
            asset_role="consumer",
            asset_type="city_load",
            region_id=1,
            region_code="DE-NORTH",
            rated_power_kw=180_000,
            operating_status="online",
            is_renewable=False,
            is_weather_dependent=False,
            is_dispatchable=False,
            can_store_energy=False,
        ),
        SimulationAsset(
            asset_id=8,
            asset_code="S-IND-001",
            asset_role="consumer",
            asset_type="industrial_load",
            region_id=2,
            region_code="DE-SOUTH",
            rated_power_kw=130_000,
            operating_status="online",
            is_renewable=False,
            is_weather_dependent=False,
            is_dispatchable=False,
            can_store_energy=False,
        ),
    ]

    intervals = simulate_assets_intervals(
        config=config,
        assets=assets,
    )

    assert len(intervals) == len(assets) * config.total_intervals

    assert {interval.asset_id for interval in intervals} == {
        asset.asset_id for asset in assets
    }

    assert all(isinstance(interval, PowerIntervalDraft) for interval in intervals)

    assert all(
        interval.avg_active_power_kw is None or interval.avg_active_power_kw >= 0
        for interval in intervals
    )
