from datetime import datetime

import pytest

from src.balance.service import build_balance_summary, build_balance_series


@pytest.mark.balance
def test_build_balance_summary_from_measurements():
    start_time = datetime(2026, 9, 8, 10, 0)
    end_time = datetime(2026, 9, 8, 10, 30)

    database_assets = [
        {
            "asset_id": 1,
            "asset_role": "producer",
            "asset_type": "solar_park",
        },
        {
            "asset_id": 2,
            "asset_role": "consumer",
            "asset_type": "city_load",
        },
    ]

    measurements = [
        # Producer: constant 100 MW
        {
            "asset_id": 1,
            "measurement_time": datetime(2026, 9, 8, 10, 0),
            "active_power_kw": 100_000.0,
            "source": "simulation",
            "quality_status": "valid",
        },
        {
            "asset_id": 1,
            "measurement_time": datetime(2026, 9, 8, 10, 15),
            "active_power_kw": 100_000.0,
            "source": "simulation",
            "quality_status": "valid",
        },
        {
            "asset_id": 1,
            "measurement_time": datetime(2026, 9, 8, 10, 30),
            "active_power_kw": 100_000.0,
            "source": "simulation",
            "quality_status": "valid",
        },
        # Consumer: constant 80 MW
        {
            "asset_id": 2,
            "measurement_time": datetime(2026, 9, 8, 10, 0),
            "active_power_kw": 80_000.0,
            "source": "simulation",
            "quality_status": "valid",
        },
        {
            "asset_id": 2,
            "measurement_time": datetime(2026, 9, 8, 10, 15),
            "active_power_kw": 80_000.0,
            "source": "simulation",
            "quality_status": "valid",
        },
        {
            "asset_id": 2,
            "measurement_time": datetime(2026, 9, 8, 10, 30),
            "active_power_kw": 80_000.0,
            "source": "simulation",
            "quality_status": "valid",
        },
    ]

    balance_series = build_balance_series(
        measurements=measurements,
        database_assets=database_assets,
        start_time=start_time,
        end_time=end_time,
        interval_minutes=15,
    )

    summary = build_balance_summary(balance_series)

    assert summary.start_time == start_time
    assert summary.end_time == end_time

    assert summary.total_production_energy_kwh == pytest.approx(50_000.0)
    assert summary.total_consumption_energy_kwh == pytest.approx(40_000.0)
    assert summary.total_net_energy_kwh == pytest.approx(10_000.0)

    assert summary.quality_status == "valid"


@pytest.mark.balance
def test_build_balance_summary_rejects_non_divisible_period():
    start_time = datetime(2026, 9, 8, 10, 0)
    end_time = datetime(2026, 9, 8, 10, 20)

    with pytest.raises(
        ValueError,
        match="Balance period must be divisible by interval_minutes",
    ):
        build_balance_summary(
            build_balance_series(
                measurements=[],
                database_assets=[],
                start_time=start_time,
                end_time=end_time,
                interval_minutes=15,
            )
        )
