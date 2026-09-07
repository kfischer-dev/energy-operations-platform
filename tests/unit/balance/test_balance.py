from dataclasses import replace
from datetime import datetime, timedelta

import pytest

from src.balance.balance import (
    calculate_balance_interval,
    calculate_balance_series,
    calculate_energy_mix,
)
from src.balance.models import BalanceAsset
from src.measurements.models import PowerIntervalDraft


INTERVAL_START = datetime(2026, 9, 7, 10, 0)
INTERVAL_END = INTERVAL_START + timedelta(minutes=15)


def create_interval(
    asset_id: int,
    avg_power_kw: float,
    *,
    interval_start: datetime = INTERVAL_START,
    interval_end: datetime = INTERVAL_END,
    quality_status: str = "valid",
) -> PowerIntervalDraft:
    interval_hours = (interval_end - interval_start).total_seconds() / 3600
    energy_kwh = avg_power_kw * interval_hours

    return PowerIntervalDraft(
        asset_id=asset_id,
        interval_start=interval_start,
        interval_end=interval_end,
        avg_active_power_kw=avg_power_kw,
        energy_kwh=energy_kwh,
        quality_status=quality_status,
        aggregation_method="trapezoidal",
        source_measurement_count=2,
        valid_measurement_count=2,
        coverage_ratio=1.0,
    )


@pytest.fixture
def assets() -> dict[int, BalanceAsset]:
    return {
        1: BalanceAsset(
            asset_role="producer",
            asset_type="solar_park",
        ),
        2: BalanceAsset(
            asset_role="producer",
            asset_type="solar_park",
        ),
        3: BalanceAsset(
            asset_role="producer",
            asset_type="wind_park",
        ),
        4: BalanceAsset(
            asset_role="consumer",
            asset_type="city_load",
        ),
        5: BalanceAsset(
            asset_role="consumer",
            asset_type="industrial_load",
        ),
        6: BalanceAsset(
            asset_role="storage",
            asset_type="battery_storage",
        ),
        7: BalanceAsset(
            asset_role="grid",
            asset_type="grid_connection",
        ),
    }


@pytest.mark.balance
def test_calculate_balance_interval_sums_assets_by_role(assets):
    intervals = [
        create_interval(1, 40_000.0),  # 10,000 kWh
        create_interval(3, 60_000.0),  # 15,000 kWh
        create_interval(4, 80_000.0),  # 20,000 kWh
    ]

    balance = calculate_balance_interval(intervals, assets)

    assert balance.avg_production_power_kw == 100_000.0
    assert balance.avg_consumption_power_kw == 80_000.0
    assert balance.avg_net_power_kw == 20_000.0

    assert balance.production_energy_kwh == 25_000.0
    assert balance.consumption_energy_kwh == 20_000.0
    assert balance.net_energy_kwh == 5_000.0

    assert balance.quality_status == "valid"


@pytest.mark.balance
def test_calculate_balance_interval_allows_negative_net_balance(assets):
    intervals = [
        create_interval(1, 40_000.0),  # 10,000 kWh
        create_interval(4, 100_000.0),  # 25,000 kWh
    ]

    balance = calculate_balance_interval(intervals, assets)

    assert balance.avg_production_power_kw == 40_000.0
    assert balance.avg_consumption_power_kw == 100_000.0
    assert balance.avg_net_power_kw == -60_000.0

    assert balance.production_energy_kwh == 10_000.0
    assert balance.consumption_energy_kwh == 25_000.0
    assert balance.net_energy_kwh == -15_000.0


@pytest.mark.balance
def test_calculate_balance_interval_ignores_storage_and_grid(assets):
    intervals = [
        create_interval(
            1,
            40_000.0,
            quality_status="valid",
        ),  # producer: 10,000 kWh
        create_interval(
            4,
            80_000.0,
            quality_status="valid",
        ),  # consumer: 20,000 kWh
        create_interval(
            6,
            50_000.0,
            quality_status="invalid",
        ),  # storage -> ignored
        create_interval(
            7,
            30_000.0,
            quality_status="incomplete",
        ),  # grid -> ignored
    ]

    balance = calculate_balance_interval(intervals, assets)

    assert balance.avg_production_power_kw == 40_000.0
    assert balance.avg_consumption_power_kw == 80_000.0
    assert balance.avg_net_power_kw == -40_000.0

    assert balance.production_energy_kwh == 10_000.0
    assert balance.consumption_energy_kwh == 20_000.0
    assert balance.net_energy_kwh == -10_000.0

    assert balance.quality_status == "valid"


@pytest.mark.balance
def test_calculate_balance_interval_uses_worst_relevant_quality_status(assets):
    intervals = [
        create_interval(
            1,
            40_000.0,
            quality_status="valid",
        ),
        create_interval(
            3,
            60_000.0,
            quality_status="incomplete",
        ),
        create_interval(
            4,
            80_000.0,
            quality_status="estimated",
        ),
    ]

    balance = calculate_balance_interval(intervals, assets)

    assert balance.quality_status == "incomplete"


@pytest.mark.balance
def test_calculate_balance_interval_rejects_duplicate_asset(assets):
    intervals = [
        create_interval(1, 40_000.0),
        create_interval(1, 45_000.0),
        create_interval(4, 80_000.0),
    ]

    with pytest.raises(
        ValueError,
        match="Duplicate interval for asset 1",
    ):
        calculate_balance_interval(intervals, assets)


@pytest.mark.parametrize(
    "missing_field",
    [
        "avg_active_power_kw",
        "energy_kwh",
    ],
)
@pytest.mark.balance
def test_calculate_balance_interval_rejects_missing_power_or_energy(
    assets,
    missing_field,
):
    interval = create_interval(1, 40_000.0)

    interval_with_missing_value = replace(
        interval,
        **{missing_field: None},
    )

    with pytest.raises(
        ValueError,
        match="Missing power or energy data for asset 1",
    ):
        calculate_balance_interval(
            [interval_with_missing_value],
            assets,
        )


@pytest.mark.balance
def test_calculate_balance_interval_rejects_different_interval_bounds(assets):
    intervals = [
        create_interval(1, 40_000.0),
        create_interval(
            3,
            60_000.0,
            interval_end=INTERVAL_END + timedelta(minutes=15),
        ),
    ]

    with pytest.raises(
        ValueError,
        match="same start and end time",
    ):
        calculate_balance_interval(intervals, assets)


@pytest.mark.balance
def test_calculate_balance_interval_rejects_missing_asset_metadata(assets):
    intervals = [
        create_interval(99, 40_000.0),
    ]

    with pytest.raises(
        ValueError,
        match="Missing balance metadata for asset 99",
    ):
        calculate_balance_interval(intervals, assets)


@pytest.mark.balance
def test_calculate_energy_mix_groups_producers_over_time_by_asset_type(assets):
    second_interval_start = INTERVAL_END
    second_interval_end = second_interval_start + timedelta(minutes=15)

    intervals = [
        # Solar asset 1
        create_interval(
            1,
            40_000.0,
        ),  # 10,000 kWh
        create_interval(
            1,
            48_000.0,
            interval_start=second_interval_start,
            interval_end=second_interval_end,
        ),  # 12,000 kWh

        # Solar asset 2
        create_interval(
            2,
            20_000.0,
        ),  # 5,000 kWh

        # Wind asset
        create_interval(
            3,
            60_000.0,
        ),  # 15,000 kWh

        # Consumer -> must not be part of producer mix
        create_interval(
            4,
            80_000.0,
        ),  # 20,000 kWh
    ]

    energy_mix = calculate_energy_mix(
        intervals,
        assets,
        "producer",
    )

    assert energy_mix.asset_role == "producer"
    assert energy_mix.start_time == INTERVAL_START
    assert energy_mix.end_time == second_interval_end

    assert energy_mix.total_energy_kwh == 42_000.0
    assert energy_mix.quality_status == "valid"

    assert len(energy_mix.contributions) == 2

    solar = next(
        contribution
        for contribution in energy_mix.contributions
        if contribution.asset_type == "solar_park"
    )

    wind = next(
        contribution
        for contribution in energy_mix.contributions
        if contribution.asset_type == "wind_park"
    )

    assert solar.energy_kwh == 27_000.0
    assert solar.share_percent == pytest.approx(
        27_000.0 / 42_000.0 * 100
    )
    assert solar.asset_count == 2

    assert wind.energy_kwh == 15_000.0
    assert wind.share_percent == pytest.approx(
        15_000.0 / 42_000.0 * 100
    )
    assert wind.asset_count == 1


@pytest.mark.balance
def test_calculate_balance_series_groups_and_sorts_time_intervals(assets):
    second_interval_start = INTERVAL_END
    second_interval_end = second_interval_start + timedelta(minutes=15)

    intervals = [
        # Input intentionally not sorted chronologically

        # Second interval: 10:15–10:30
        create_interval(
            4,
            72_000.0,
            interval_start=second_interval_start,
            interval_end=second_interval_end,
        ),  # consumer: 18,000 kWh
        create_interval(
            1,
            44_000.0,
            interval_start=second_interval_start,
            interval_end=second_interval_end,
        ),  # producer: 11,000 kWh

        # First interval: 10:00–10:15
        create_interval(
            3,
            60_000.0,
        ),  # producer: 15,000 kWh
        create_interval(
            4,
            80_000.0,
        ),  # consumer: 20,000 kWh

        # Second interval
        create_interval(
            3,
            64_000.0,
            interval_start=second_interval_start,
            interval_end=second_interval_end,
        ),  # producer: 16,000 kWh

        # First interval
        create_interval(
            1,
            40_000.0,
        ),  # producer: 10,000 kWh
    ]

    balance_series = calculate_balance_series(
        intervals,
        assets,
    )

    assert len(balance_series) == 2

    first_balance = balance_series[0]
    second_balance = balance_series[1]

    # First interval: 10:00–10:15
    assert first_balance.interval_start == INTERVAL_START
    assert first_balance.interval_end == INTERVAL_END

    assert first_balance.avg_production_power_kw == 100_000.0
    assert first_balance.avg_consumption_power_kw == 80_000.0
    assert first_balance.avg_net_power_kw == 20_000.0

    assert first_balance.production_energy_kwh == 25_000.0
    assert first_balance.consumption_energy_kwh == 20_000.0
    assert first_balance.net_energy_kwh == 5_000.0

    # Second interval: 10:15–10:30
    assert second_balance.interval_start == second_interval_start
    assert second_balance.interval_end == second_interval_end

    assert second_balance.avg_production_power_kw == 108_000.0
    assert second_balance.avg_consumption_power_kw == 72_000.0
    assert second_balance.avg_net_power_kw == 36_000.0

    assert second_balance.production_energy_kwh == 27_000.0
    assert second_balance.consumption_energy_kwh == 18_000.0
    assert second_balance.net_energy_kwh == 9_000.0
