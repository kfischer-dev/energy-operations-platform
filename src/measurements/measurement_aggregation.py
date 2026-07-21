from datetime import datetime

from src.measurements.models import (
    PowerIntervalDraft,
    PowerMeasurement,
    PowerSegment,
    PowerSupportPoint,
)


def create_interpolated_support_point(
    left_measurement: PowerMeasurement,
    right_measurement: PowerMeasurement,
    target_time: datetime,
) -> PowerSupportPoint:
    """Creates a linearly interpolated support point."""

    left_time = left_measurement.measurement_time
    right_time = right_measurement.measurement_time

    total_duration_seconds = (right_time - left_time).total_seconds()

    if total_duration_seconds <= 0:
        raise ValueError("Right measurement must be later than left measurement.")

    if not left_time <= target_time <= right_time:
        raise ValueError("Target time must lie between the support measurements.")

    elapsed_seconds = (target_time - left_time).total_seconds()
    interpolation_ratio = elapsed_seconds / total_duration_seconds
    interpolated_power_kw = left_measurement.active_power_kw + (
        right_measurement.active_power_kw - left_measurement.active_power_kw
    ) * interpolation_ratio

    return PowerSupportPoint(
        timestamp=target_time,
        active_power_kw=interpolated_power_kw,
        point_type="interpolated",
        is_interpolated=True,
    )


def validate_aggregation_inputs(
    asset_id: int,
    interval_start: datetime,
    interval_end: datetime,
    measurements: list[PowerMeasurement],
) -> None:
    """Validates inputs for the aggregation function."""

    if interval_end <= interval_start:
        raise ValueError("Interval end time must be after interval start time.")

    if len(measurements) <= 1:
        raise ValueError("At least two measurements are required for aggregation.")

    for measurement in measurements:
        if measurement.asset_id != asset_id:
            raise ValueError(
                f"Measurement asset_id {measurement.asset_id} does not match the provided asset_id {asset_id}."
            )

    measurement_times = [measurement.measurement_time for measurement in measurements]

    if len(measurement_times) != len(set(measurement_times)):
        raise ValueError("Duplicate measurement times are not allowed within the same interval.")


def sort_measurements_by_time(
    measurements: list[PowerMeasurement],
) -> list[PowerMeasurement]:
    """Sorts measurements by their measurement time."""

    return sorted(measurements, key=lambda measurement: measurement.measurement_time)


def select_interval_measurements(
    measurements: list[PowerMeasurement],
    interval_start: datetime,
    interval_end: datetime,
) -> tuple[
    PowerMeasurement | None,
    list[PowerMeasurement],
    PowerMeasurement | None,
]:
    """Selects left, internal, and right support measurements."""

    sorted_measurements = sort_measurements_by_time(measurements)

    left_candidates = [
        measurement for measurement in sorted_measurements
        if measurement.measurement_time <= interval_start
    ]
    left_support = left_candidates[-1] if left_candidates else None

    internal_measurements = [
        measurement for measurement in sorted_measurements
        if interval_start < measurement.measurement_time < interval_end
    ]

    right_candidates = [
        measurement for measurement in sorted_measurements
        if measurement.measurement_time >= interval_end
    ]
    right_support = right_candidates[0] if right_candidates else None

    return left_support, internal_measurements, right_support


def create_measured_support_point(
    measurement: PowerMeasurement,
) -> PowerSupportPoint:
    """Creates a support point from a measured value."""

    return PowerSupportPoint(
        timestamp=measurement.measurement_time,
        active_power_kw=measurement.active_power_kw,
        point_type="measured",
        is_interpolated=False,
    )


def create_start_point(
    left_support: PowerMeasurement | None,
    first_measurement_after_start: PowerMeasurement | None,
    interval_start: datetime,
) -> PowerSupportPoint | None:
    """Creates the support point at the interval start."""

    if left_support is None or first_measurement_after_start is None:
        return None

    if left_support.measurement_time == interval_start:
        return create_measured_support_point(left_support)

    return create_interpolated_support_point(
        left_measurement=left_support,
        right_measurement=first_measurement_after_start,
        target_time=interval_start,
    )


def create_end_point(
    last_measurement_before_end: PowerMeasurement | None,
    right_support: PowerMeasurement | None,
    interval_end: datetime,
) -> PowerSupportPoint | None:
    """Creates the support point at the interval end."""

    if last_measurement_before_end is None or right_support is None:
        return None

    if right_support.measurement_time == interval_end:
        return create_measured_support_point(right_support)

    return create_interpolated_support_point(
        left_measurement=last_measurement_before_end,
        right_measurement=right_support,
        target_time=interval_end,
    )


def build_calculation_points(
    left_support: PowerMeasurement | None,
    internal_measurements: list[PowerMeasurement],
    right_support: PowerMeasurement | None,
    interval_start: datetime,
    interval_end: datetime,
) -> list[PowerSupportPoint]:
    """Builds the sorted support-point list used for aggregation."""

    first_measurement_after_start = internal_measurements[0] if internal_measurements else right_support
    last_measurement_before_end = internal_measurements[-1] if internal_measurements else left_support

    start_point = create_start_point(
        left_support=left_support,
        first_measurement_after_start=first_measurement_after_start,
        interval_start=interval_start,
    )

    end_point = create_end_point(
        last_measurement_before_end=last_measurement_before_end,
        right_support=right_support,
        interval_end=interval_end,
    )

    internal_points = [
        create_measured_support_point(measurement)
        for measurement in internal_measurements
    ]

    calculation_points: list[PowerSupportPoint] = []

    if start_point is not None:
        calculation_points.append(start_point)

    calculation_points.extend(internal_points)

    if end_point is not None:
        calculation_points.append(end_point)

    return sorted(calculation_points, key=lambda point: point.timestamp)


def build_segments(
    calculation_points: list[PowerSupportPoint],
) -> list[PowerSegment]:
    """Builds adjacent power segments from calculation points."""

    return [
        PowerSegment(
            start_point=calculation_points[index],
            end_point=calculation_points[index + 1],
        )
        for index in range(len(calculation_points) - 1)
    ]


def calculate_segment_energy_kwh(segment: PowerSegment) -> float:
    """Calculates segment energy using the trapezoidal rule."""

    duration_hours = (segment.end_point.timestamp - segment.start_point.timestamp).total_seconds() / 3600

    if duration_hours <= 0:
        raise ValueError("Segment end time must be after segment start time.")

    average_power_kw = (segment.start_point.active_power_kw + segment.end_point.active_power_kw) / 2

    return average_power_kw * duration_hours


def calculate_interval_energy_kwh(
    segments: list[PowerSegment],
) -> float:
    """Calculates the total energy of all segments."""

    return sum(calculate_segment_energy_kwh(segment) for segment in segments)


def calculate_covered_duration_seconds(
    segments: list[PowerSegment],
) -> float:
    """Calculates the duration covered by all segments."""

    total_duration_seconds = 0.0

    for segment in segments:
        duration_seconds = (segment.end_point.timestamp - segment.start_point.timestamp).total_seconds()

        if duration_seconds <= 0:
            raise ValueError("Segment end time must be after segment start time.")

        total_duration_seconds += duration_seconds

    return total_duration_seconds


def calculate_interval_avg_power_kw(
    energy_kwh: float,
    covered_duration_seconds: float,
) -> float | None:
    """Calculates time-weighted average power for the covered duration."""

    covered_duration_hours = covered_duration_seconds / 3600

    if covered_duration_hours <= 0:
        return None

    return energy_kwh / covered_duration_hours


def determine_quality_status(coverage_ratio: float) -> str:
    """Determines interval quality from its coverage ratio."""

    if coverage_ratio <= 0.0:
        return "invalid"

    if coverage_ratio >= 1.0:
        return "valid"

    return "incomplete"


def aggregate_measurements_for_interval(
    asset_id: int,
    interval_start: datetime,
    interval_end: datetime,
    measurements: list[PowerMeasurement],
) -> PowerIntervalDraft:
    """Aggregates power measurements for a given interval."""

    validate_aggregation_inputs(
        asset_id=asset_id,
        interval_start=interval_start,
        interval_end=interval_end,
        measurements=measurements,
    )

    source_measurement_count = len(measurements)

    usable_measurements = [
        measurement for measurement in measurements
        if measurement.quality_status != "invalid"
    ]

    left_support, internal_measurements, right_support = (
        select_interval_measurements(
            measurements=usable_measurements,
            interval_start=interval_start,
            interval_end=interval_end,
        )
    )

    valid_measurement_count = (
        len(internal_measurements)
        + int(left_support is not None)
        + int(right_support is not None)
    )

    calculation_points = build_calculation_points(
        left_support=left_support,
        internal_measurements=internal_measurements,
        right_support=right_support,
        interval_start=interval_start,
        interval_end=interval_end,
    )

    segments = build_segments(calculation_points)
    total_interval_seconds = (interval_end - interval_start).total_seconds()
    covered_duration_seconds = calculate_covered_duration_seconds(segments)

    if not segments:
        energy_kwh = None
        avg_active_power_kw = None
    else:
        energy_kwh = calculate_interval_energy_kwh(segments)
        avg_active_power_kw = calculate_interval_avg_power_kw(
            energy_kwh=energy_kwh,
            covered_duration_seconds=covered_duration_seconds,
        )

    coverage_ratio = max(0.0, min(covered_duration_seconds / total_interval_seconds, 1.0))
    quality_status = determine_quality_status(coverage_ratio)

    return PowerIntervalDraft(
        asset_id=asset_id,
        interval_start=interval_start,
        interval_end=interval_end,
        avg_active_power_kw=avg_active_power_kw,
        energy_kwh=energy_kwh,
        quality_status=quality_status,
        aggregation_method="linear_interpolation_trapezoidal",
        source_measurement_count=source_measurement_count,
        valid_measurement_count=valid_measurement_count,
        coverage_ratio=coverage_ratio,
    )


def load_measurements_for_interval_aggregation(
    asset_id: int,
    interval_start: datetime,
    interval_end: datetime,
) -> list[PowerMeasurement]:
    """Loads boundary-aware power measurements for an interval."""

    # Database implementation follows in a later block.
    raise NotImplementedError

# Test Functions

def run_manual_aggregation_test() -> None:
    """Runs a simple manual smoke test for interval aggregation."""

    measurements = [
        PowerMeasurement(
            asset_id=1,
            measurement_time=datetime(2026, 7, 21, 9, 58),
            active_power_kw=40.0,
            source="database",
        ),
        PowerMeasurement(
            asset_id=1,
            measurement_time=datetime(2026, 7, 21, 10, 5),
            active_power_kw=50.0,
            source="database",
        ),
        PowerMeasurement(
            asset_id=1,
            measurement_time=datetime(2026, 7, 21, 10, 12),
            active_power_kw=30.0,
            source="database",
        ),
        PowerMeasurement(
            asset_id=1,
            measurement_time=datetime(2026, 7, 21, 10, 17),
            active_power_kw=45.0,
            source="database",
        ),
    ]

    result = aggregate_measurements_for_interval(
        asset_id=1,
        interval_start=datetime(2026, 7, 21, 10, 0),
        interval_end=datetime(2026, 7, 21, 10, 15),
        measurements=measurements,
    )

    print(result)

    assert result.asset_id == 1
    assert result.interval_start == datetime(2026, 7, 21, 10, 0)
    assert result.interval_end == datetime(2026, 7, 21, 10, 15)
    assert result.coverage_ratio == 1.0
    assert result.quality_status == "valid"
    assert result.energy_kwh is not None
    assert result.avg_active_power_kw is not None

    print("Manual aggregation test passed.")

if __name__ == "__main__":
    run_manual_aggregation_test()