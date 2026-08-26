from src.measurements.measurement_aggregation import aggregate_measurements_for_interval
from src.measurements.models import PowerMeasurement


def map_measurements_to_power_measurements(measurements: list[dict]) -> list[PowerMeasurement]:
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
    measurements,
    asset_id,
    start_time,
    end_time,
):
    power_measurements = map_measurements_to_power_measurements(measurements)

    period_measurements = [
        measurement
        for measurement in power_measurements
        if start_time <= measurement.measurement_time <= end_time
    ]

    period_interval = aggregate_measurements_for_interval(
        asset_id=asset_id,
        interval_start=start_time,
        interval_end=end_time,
        measurements=power_measurements,
    )

    min_measured_power_kw = min(
        (
            measurement.active_power_kw
            for measurement in period_measurements
        ),
        default=None,
    )

    max_measured_power_kw = max(
        (
            measurement.active_power_kw
            for measurement in period_measurements
        ),
        default=None,
    )

    return {
        "period_start": start_time,
        "period_end": end_time,
        "measurement_count": len(period_measurements),
        "average_power_kw": period_interval.avg_active_power_kw,
        "min_measured_power_kw": min_measured_power_kw,
        "max_measured_power_kw": max_measured_power_kw,
        "total_energy_kwh": period_interval.energy_kwh,
        "coverage_ratio": period_interval.coverage_ratio,
    }