from collections import defaultdict
from datetime import datetime
from typing import Literal

from src.balance.balance import (
    calculate_balance_series,
    calculate_balance_summary,
    calculate_energy_mix,
)
from src.balance.models import BalanceAsset, BalanceSummary, EnergyMix
from src.measurements.measurement_aggregation import (
    aggregate_measurements_for_intervals,
)
from src.measurements.models import PowerMeasurement
from src.measurements.service import map_measurements_to_power_measurements


def _convert_database_assets_to_balance_assets(
    database_assets,
) -> dict[int, BalanceAsset]:
    """Map database asset records to BalanceAsset metadata by asset ID."""
    balance_assets = {}

    for database_asset in database_assets:
        balance_assets[database_asset["asset_id"]] = BalanceAsset(
            asset_role=database_asset["asset_role"],
            asset_type=database_asset["asset_type"],
        )

    return balance_assets


def _create_power_measurement_dict(
    power_measurements: list[PowerMeasurement],
) -> dict[int, list[PowerMeasurement]]:
    power_measurement_dict = defaultdict(list)
    for power_measurement in power_measurements:
        power_measurement_dict[power_measurement.asset_id].append(power_measurement)
    return power_measurement_dict


def _build_measurement_intervals(
    measurements: list[dict],
    start_time: datetime,
    end_time: datetime,
    interval_minutes: int,
):
    power_measurements = map_measurements_to_power_measurements(measurements)
    power_measurement_dict = _create_power_measurement_dict(power_measurements)

    intervals = []

    for asset_id, asset_measurements in power_measurement_dict.items():
        intervals.extend(
            aggregate_measurements_for_intervals(
                asset_id=asset_id,
                measurements=asset_measurements,
                start_time=start_time,
                end_time=end_time,
                interval_minutes=interval_minutes,
            )
        )

    return intervals


def build_balance_series(
    measurements: list[dict],
    database_assets: list[dict],
    start_time: datetime,
    end_time: datetime,
    interval_minutes: int = 15,
) -> list[dict]:

    if end_time <= start_time:
        raise ValueError("End time must be after start time.")

    period_minutes = (end_time - start_time).total_seconds() / 60

    if period_minutes % interval_minutes != 0:
        raise ValueError("Balance period must be divisible by interval_minutes.")

    balance_assets = _convert_database_assets_to_balance_assets(database_assets)

    intervals = _build_measurement_intervals(
        measurements=measurements,
        start_time=start_time,
        end_time=end_time,
        interval_minutes=interval_minutes,
    )

    return calculate_balance_series(intervals, balance_assets)


def build_balance_summary(
    balance_series: list[dict],
) -> BalanceSummary:
    return calculate_balance_summary(balance_series)


def build_energy_mix(
    measurements: list[dict],
    database_assets: list[dict],
    start_time: datetime,
    end_time: datetime,
    asset_role: Literal["producer", "consumer"],
    interval_minutes: int = 15,
) -> EnergyMix:
    balance_assets = _convert_database_assets_to_balance_assets(database_assets)

    intervals = _build_measurement_intervals(
        measurements=measurements,
        start_time=start_time,
        end_time=end_time,
        interval_minutes=interval_minutes,
    )

    return calculate_energy_mix(
        intervals=intervals,
        assets=balance_assets,
        asset_role=asset_role,
    )
