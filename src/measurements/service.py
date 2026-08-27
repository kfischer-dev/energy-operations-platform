from datetime import datetime

from src.measurements.measurement_aggregation import aggregate_measurements_for_interval
from src.measurements.models import PowerMeasurement


def map_measurements_to_power_measurements(
    measurements: list[dict],
) -> list[PowerMeasurement]:
    """Map measurement dictionaries to PowerMeasurement domain objects."""

    return [
        PowerMeasurement(
            asset_id=measurement["asset_id"],
            measurement_time=measurement["measurement_time"],
            active_power_kw=measurement["active_power_kw"],
            source=measurement["source"],
            quality_status=measurement["quality_status"],
        )
        for measurement in measurements
    ]


def calculate_asset_kpis(
    measurements: list[dict],
    asset_id: int,
    start_time: datetime,
    end_time: datetime,
) -> dict[str, object]:
    """Calculate period-based KPIs for one asset.

    Measured min/max values and measurement count use only measurements inside
    the requested period. Average power, energy, and coverage are derived from
    interval aggregation and may use surrounding measurements as support points.
    If fewer than two usable measurements are available, interval-based KPIs
    cannot be calculated.
    """

    power_measurements = map_measurements_to_power_measurements(measurements)

    period_measurements = [
        measurement
        for measurement in power_measurements
        if start_time <= measurement.measurement_time <= end_time
    ]

    if len(power_measurements) >= 2:
        period_interval = aggregate_measurements_for_interval(
            asset_id=asset_id,
            interval_start=start_time,
            interval_end=end_time,
            measurements=power_measurements,
        )

        avg_active_power_kw = period_interval.avg_active_power_kw
        total_energy_kwh = period_interval.energy_kwh
        coverage_ratio = period_interval.coverage_ratio

    else:
        avg_active_power_kw = None
        total_energy_kwh = None
        coverage_ratio = 0.0

    min_measured_power_kw = min(
        (measurement.active_power_kw for measurement in period_measurements),
        default=None,
    )

    max_measured_power_kw = max(
        (measurement.active_power_kw for measurement in period_measurements),
        default=None,
    )

    return {
        "period_start": start_time,
        "period_end": end_time,
        "measurement_count": len(period_measurements),
        "avg_active_power_kw": avg_active_power_kw,
        "min_measured_power_kw": min_measured_power_kw,
        "max_measured_power_kw": max_measured_power_kw,
        "total_energy_kwh": total_energy_kwh,
        "coverage_ratio": coverage_ratio,
    }


def calculate_kpis_for_all_measurements(
    measurements: list[dict],
    start_time: datetime,
    end_time: datetime,
) -> dict[str, object]:
    """Calculate global period-based KPIs across all assets.

    Measurements are grouped by asset first so that each asset is aggregated
    independently. The resulting asset KPIs are then combined into one global
    KPI summary for the requested period.
    """

    measurements_by_asset: dict[int, list[dict]] = {}

    for measurement in measurements:
        asset_id = measurement["asset_id"]
        if asset_id not in measurements_by_asset:
            measurements_by_asset[asset_id] = []

        measurements_by_asset[asset_id].append(measurement)

    asset_kpis: dict[int, dict[str, object]] = {}

    for asset_id, asset_measurements in measurements_by_asset.items():
        asset_kpis[asset_id] = calculate_asset_kpis(
            measurements=asset_measurements,
            asset_id=asset_id,
            start_time=start_time,
            end_time=end_time,
        )

    measurement_count = sum(kpis["measurement_count"] for kpis in asset_kpis.values())

    total_energy_kwh = sum(
        kpis["total_energy_kwh"]
        for kpis in asset_kpis.values()
        if kpis["total_energy_kwh"] is not None
    )

    min_measured_power_kw = min(
        (
            kpis["min_measured_power_kw"]
            for kpis in asset_kpis.values()
            if kpis["min_measured_power_kw"] is not None
        ),
        default=None,
    )

    max_measured_power_kw = max(
        (
            kpis["max_measured_power_kw"]
            for kpis in asset_kpis.values()
            if kpis["max_measured_power_kw"] is not None
        ),
        default=None,
    )

    avg_active_power_kw = sum(
        kpis["avg_active_power_kw"]
        for kpis in asset_kpis.values()
        if kpis["avg_active_power_kw"] is not None
    )

    coverage_ratio = (
        sum(
            kpis["coverage_ratio"]
            for kpis in asset_kpis.values()
            if kpis["coverage_ratio"] is not None
        )
        / len(asset_kpis)
        if asset_kpis
        else None
    )

    return {
        "period_start": start_time,
        "period_end": end_time,
        "measurement_count": measurement_count,
        "avg_active_power_kw": avg_active_power_kw,
        "min_measured_power_kw": min_measured_power_kw,
        "max_measured_power_kw": max_measured_power_kw,
        "total_energy_kwh": total_energy_kwh,
        "coverage_ratio": coverage_ratio,
    }
