"""Core calculations for portfolio energy balance and energy mix."""

from collections import defaultdict
from collections.abc import Sequence
from typing import Literal

from src.balance.models import (
    BalanceAsset,
    BalanceInterval,
    BalanceQualityStatus,
    BalanceSummary,
    EnergyMix,
    EnergyMixContribution,
)
from src.measurements.models import PowerIntervalDraft


def _validate_interval_bounds(intervals: list[PowerIntervalDraft]) -> None:
    """Ensure all intervals belong to exactly the same time window."""

    interval_bounds = {
        (interval.interval_start, interval.interval_end) for interval in intervals
    }
    if len(interval_bounds) != 1:
        raise ValueError("All intervals must have the same start and end time.")


def _get_asset(asset_id: int, assets: dict[int, BalanceAsset]) -> BalanceAsset:
    """Return balance metadata for an asset or raise a domain-level error."""

    try:
        return assets[asset_id]
    except KeyError as error:
        raise ValueError(f"Missing balance metadata for asset {asset_id}.") from error


def _combined_quality_status(
    intervals: Sequence[PowerIntervalDraft | BalanceInterval],
) -> BalanceQualityStatus:
    """Return the worst quality status across the supplied intervals."""

    priority = {
        "valid": 0,
        "estimated": 1,
        "incomplete": 2,
        "invalid": 3,
    }

    return max(
        (interval.quality_status for interval in intervals),
        key=priority.__getitem__,
    )


def _group_intervals_by_asset_type(
    intervals: list[PowerIntervalDraft],
    assets: dict[int, BalanceAsset],
) -> dict[str, list[PowerIntervalDraft]]:
    """Group power intervals by the technical type of their asset."""

    grouped_intervals: defaultdict[str, list[PowerIntervalDraft]] = defaultdict(list)

    for interval in intervals:
        asset = _get_asset(interval.asset_id, assets)
        grouped_intervals[asset.asset_type].append(interval)

    return dict(grouped_intervals)


def calculate_balance_interval(
    intervals: list[PowerIntervalDraft], assets: dict[int, BalanceAsset]
) -> BalanceInterval:
    """Calculate production, consumption, and net values for one time window.

    Storage and grid assets are intentionally excluded from the v0.13 balance.
    """

    _validate_interval_bounds(intervals)

    avg_production_power_kw = 0.0
    production_energy_kwh = 0.0
    avg_consumption_power_kw = 0.0
    consumption_energy_kwh = 0.0

    # Each asset may contribute at most one interval to a time window.
    checked_asset_ids = set()
    relevant_intervals = []

    for interval in intervals:
        if interval.asset_id in checked_asset_ids:
            raise ValueError(
                f"Duplicate interval for asset {interval.asset_id} detected."
            )

        checked_asset_ids.add(interval.asset_id)

        role = _get_asset(interval.asset_id, assets).asset_role
        if role in ("storage", "grid"):
            # These roles are outside the current production/consumption balance.
            continue
        elif role not in ("producer", "consumer"):
            raise ValueError(f"Asset role '{role}' is not supported by the balance.")

        avg_power_kw = interval.avg_active_power_kw
        energy_kwh = interval.energy_kwh

        if avg_power_kw is None or energy_kwh is None:
            raise ValueError(
                f"Missing power or energy data for asset {interval.asset_id}."
            )

        relevant_intervals.append(interval)

        if role == "producer":
            avg_production_power_kw += avg_power_kw
            production_energy_kwh += energy_kwh
        elif role == "consumer":
            avg_consumption_power_kw += avg_power_kw
            consumption_energy_kwh += energy_kwh

    if not relevant_intervals:
        raise ValueError(
            "No producer or consumer intervals available for balance calculation."
        )

    first_interval = intervals[0]
    return BalanceInterval(
        interval_start=first_interval.interval_start,
        interval_end=first_interval.interval_end,
        avg_production_power_kw=avg_production_power_kw,
        avg_consumption_power_kw=avg_consumption_power_kw,
        avg_net_power_kw=avg_production_power_kw - avg_consumption_power_kw,
        production_energy_kwh=production_energy_kwh,
        consumption_energy_kwh=consumption_energy_kwh,
        net_energy_kwh=production_energy_kwh - consumption_energy_kwh,
        quality_status=_combined_quality_status(relevant_intervals),
    )


def calculate_balance_series(
    intervals: list[PowerIntervalDraft],
    assets: dict[int, BalanceAsset],
) -> list[BalanceInterval]:
    """Group intervals by time window and return a chronological balance series."""

    grouped_intervals = defaultdict(list)

    for interval in intervals:
        interval_key = (
            interval.interval_start,
            interval.interval_end,
        )
        grouped_intervals[interval_key].append(interval)

    balance_series = []

    # Tuple keys sort by start time first and end time second.
    for interval_key in sorted(grouped_intervals):
        grouped_interval = grouped_intervals[interval_key]

        balance = calculate_balance_interval(
            grouped_interval,
            assets,
        )

        balance_series.append(balance)

    return balance_series


def calculate_balance_summary(
    balance_series: list[BalanceInterval],
) -> BalanceSummary:
    """Calculate energy totals and quality for a balance series."""

    if not balance_series:
        raise ValueError("Balance series must not be empty.")

    start_time = min(interval.interval_start for interval in balance_series)
    end_time = max(interval.interval_end for interval in balance_series)

    total_production_energy_kwh = sum(
        interval.production_energy_kwh for interval in balance_series
    )
    total_consumption_energy_kwh = sum(
        interval.consumption_energy_kwh for interval in balance_series
    )
    total_net_energy_kwh = total_production_energy_kwh - total_consumption_energy_kwh

    quality_status = _combined_quality_status(balance_series)

    return BalanceSummary(
        start_time=start_time,
        end_time=end_time,
        total_production_energy_kwh=total_production_energy_kwh,
        total_consumption_energy_kwh=total_consumption_energy_kwh,
        total_net_energy_kwh=total_net_energy_kwh,
        quality_status=quality_status,
    )


def calculate_energy_mix(
    intervals: list[PowerIntervalDraft],
    assets: dict[int, BalanceAsset],
    asset_role: Literal["producer", "consumer"],
) -> EnergyMix:
    """Calculate period energy contributions by asset type for one asset role."""

    relevant_intervals = [
        interval
        for interval in intervals
        if _get_asset(interval.asset_id, assets).asset_role == asset_role
    ]

    if not relevant_intervals:
        raise ValueError(f"No intervals available for asset role '{asset_role}'.")

    for interval in relevant_intervals:
        if interval.energy_kwh is None:
            raise ValueError(f"Missing energy data for asset {interval.asset_id}.")

    grouped_intervals = _group_intervals_by_asset_type(relevant_intervals, assets)

    total_energy_kwh = sum(interval.energy_kwh for interval in relevant_intervals)

    contributions = []
    for asset_type, type_intervals in grouped_intervals.items():
        energy_kwh = sum(interval.energy_kwh for interval in type_intervals)
        share_percent = (
            energy_kwh / total_energy_kwh * 100 if total_energy_kwh > 0 else 0.0
        )
        asset_count = len({interval.asset_id for interval in type_intervals})

        contributions.append(
            EnergyMixContribution(
                asset_type=asset_type,
                energy_kwh=energy_kwh,
                share_percent=share_percent,
                asset_count=asset_count,
            )
        )

    start_time = min(interval.interval_start for interval in relevant_intervals)

    end_time = max(interval.interval_end for interval in relevant_intervals)
    return EnergyMix(
        start_time=start_time,
        end_time=end_time,
        asset_role=asset_role,
        total_energy_kwh=total_energy_kwh,
        contributions=tuple(contributions),
        quality_status=_combined_quality_status(relevant_intervals),
    )
