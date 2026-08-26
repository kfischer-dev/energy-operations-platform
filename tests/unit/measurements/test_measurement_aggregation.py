from datetime import datetime, timedelta, timezone

import pytest

from src.measurements.measurement_aggregation import (
    aggregate_measurements_for_interval,
    aggregate_measurements_for_intervals,
    build_segments,
    calculate_segment_energy_kwh,
    create_interpolated_support_point,
    determine_quality_status,
)
from src.measurements.models import (
    PowerIntervalDraft,
    PowerMeasurement,
    PowerSegment,
    PowerSupportPoint,
)
from tests.factories import create_power_measurement


# ============================================================
# Aggregate Interval
# ============================================================


@pytest.mark.aggregation
def test_aggregates_fully_covered_interval() -> None:
    """Aggregates a fully covered interval using boundary measurements."""

    interval_start = datetime(2026, 7, 22, 10, 0)
    interval_end = datetime(2026, 7, 22, 10, 15)

    power_measurements = [
        create_power_measurement(interval_start, 40_000.0),
        create_power_measurement(interval_end, 60_000.0),
    ]

    power_interval = aggregate_measurements_for_interval(
        asset_id=1,
        interval_start=interval_start,
        interval_end=interval_end,
        measurements=power_measurements,
    )

    assert power_interval.avg_active_power_kw == pytest.approx(50_000.0)
    assert power_interval.energy_kwh == pytest.approx(12_500.0)
    assert power_interval.coverage_ratio == pytest.approx(1.0)
    assert power_interval.quality_status == "valid"
    assert power_interval.source_measurement_count == 2
    assert power_interval.valid_measurement_count == 2


@pytest.mark.aggregation
def test_interpolates_interval_boundaries() -> None:
    """Interpolates missing interval boundaries before aggregation."""

    interval_start = datetime(2026, 7, 22, 10, 0)
    interval_end = datetime(2026, 7, 22, 10, 15)

    power_measurements = [
        create_power_measurement(datetime(2026, 7, 22, 9, 55), 30_000.0),
        create_power_measurement(datetime(2026, 7, 22, 10, 5), 50_000.0),
        create_power_measurement(datetime(2026, 7, 22, 10, 10), 70_000.0),
        create_power_measurement(datetime(2026, 7, 22, 10, 20), 90_000.0),
    ]

    power_interval = aggregate_measurements_for_interval(
        asset_id=1,
        interval_start=interval_start,
        interval_end=interval_end,
        measurements=power_measurements,
    )

    assert power_interval.avg_active_power_kw == pytest.approx(60_000.0)
    assert power_interval.energy_kwh == pytest.approx(15_000.0)
    assert power_interval.coverage_ratio == pytest.approx(1.0)
    assert power_interval.quality_status == "valid"
    assert power_interval.source_measurement_count == 4
    assert power_interval.valid_measurement_count == 4


@pytest.mark.aggregation
def test_calculates_energy_with_trapezoidal_rule() -> None:
    """Calculates interval energy using the trapezoidal rule."""

    interval_start = datetime(2026, 7, 22, 10, 0)
    interval_end = datetime(2026, 7, 22, 10, 15)

    power_measurements = [
        create_power_measurement(interval_start, 0.0),
        create_power_measurement(datetime(2026, 7, 22, 10, 5), 60_000.0),
        create_power_measurement(interval_end, 60_000.0),
    ]

    power_interval = aggregate_measurements_for_interval(
        asset_id=1,
        interval_start=interval_start,
        interval_end=interval_end,
        measurements=power_measurements,
    )

    assert power_interval.energy_kwh == pytest.approx(12_500.0)
    assert power_interval.avg_active_power_kw == pytest.approx(50_000.0)


@pytest.mark.aggregation
def test_returns_incomplete_interval_with_partial_coverage() -> None:
    """Aggregates only the covered portion of a partially covered interval."""

    interval_start = datetime(2026, 7, 22, 10, 0)
    interval_end = datetime(2026, 7, 22, 10, 15)

    power_measurements = [
        create_power_measurement(datetime(2026, 7, 22, 10, 5), 40_000.0),
        create_power_measurement(datetime(2026, 7, 22, 10, 10), 60_000.0),
    ]

    power_interval = aggregate_measurements_for_interval(
        asset_id=1,
        interval_start=interval_start,
        interval_end=interval_end,
        measurements=power_measurements,
    )

    assert power_interval.energy_kwh == pytest.approx(4_166.6667)
    assert power_interval.avg_active_power_kw == pytest.approx(50_000.0)
    assert power_interval.coverage_ratio == pytest.approx(1 / 3)
    assert power_interval.quality_status == "incomplete"
    assert power_interval.source_measurement_count == 2
    assert power_interval.valid_measurement_count == 2


@pytest.mark.aggregation
def test_returns_invalid_interval_without_coverage() -> None:
    """Returns an invalid interval when no segment can be built."""

    interval_start = datetime(2026, 7, 22, 10, 0)
    interval_end = datetime(2026, 7, 22, 10, 15)

    power_measurements = [
        create_power_measurement(datetime(2026, 7, 22, 9, 40), 40_000.0),
        create_power_measurement(datetime(2026, 7, 22, 9, 50), 60_000.0),
    ]

    power_interval = aggregate_measurements_for_interval(
        asset_id=1,
        interval_start=interval_start,
        interval_end=interval_end,
        measurements=power_measurements,
    )
    
    assert power_interval.energy_kwh is None
    assert power_interval.avg_active_power_kw is None
    assert power_interval.coverage_ratio == pytest.approx(0.0)
    assert power_interval.quality_status == "invalid"
    assert power_interval.source_measurement_count == 1
    assert power_interval.valid_measurement_count == 1


@pytest.mark.aggregation
def test_aggregates_measurements_into_consecutive_intervals() -> None:
    """Aggregates a measurement grid into consecutive fixed-length intervals."""
    start_time = datetime(2026, 7, 22, 10, 0, tzinfo=timezone.utc)
    end_time = start_time + timedelta(hours=1)

    measurements = [
        PowerMeasurement(
            asset_id=1,
            measurement_time=start_time,
            active_power_kw=100.0,
            source="simulation",
        ),
        PowerMeasurement(
            asset_id=1,
            measurement_time=start_time + timedelta(minutes=15),
            active_power_kw=110.0,
            source="simulation",
        ),
        PowerMeasurement(
            asset_id=1,
            measurement_time=start_time + timedelta(minutes=30),
            active_power_kw=120.0,
            source="simulation",
        ),
        PowerMeasurement(
            asset_id=1,
            measurement_time=start_time + timedelta(minutes=45),
            active_power_kw=130.0,
            source="simulation",
        ),
        PowerMeasurement(
            asset_id=1,
            measurement_time=end_time,
            active_power_kw=140.0,
            source="simulation",
        ),
    ]

    intervals = aggregate_measurements_for_intervals(
        asset_id=1,
        measurements=measurements,
        start_time=start_time,
        end_time=end_time,
        interval_minutes=15,
    )

    assert len(intervals) == 4
    assert all(isinstance(interval, PowerIntervalDraft) for interval in intervals)
    assert all(interval.asset_id == 1 for interval in intervals)
    assert all(interval.quality_status == "valid" for interval in intervals)
    assert all(interval.avg_active_power_kw is not None for interval in intervals)
    assert all(interval.energy_kwh is not None for interval in intervals)

    assert intervals[0].interval_start == start_time
    assert intervals[-1].interval_end == end_time

    for current, following in zip(intervals, intervals[1:]):
        assert current.interval_end == following.interval_start


# ============================================================
# Validation
# ============================================================


@pytest.mark.aggregation
def test_sorts_unsorted_measurements() -> None:
    """Returns the same result when measurements are not chronologically sorted."""

    interval_start = datetime(2026, 7, 22, 10, 0)
    interval_end = datetime(2026, 7, 22, 10, 15)

    power_measurements = [
        create_power_measurement(interval_end, 60_000.0),
        create_power_measurement(interval_start, 40_000.0),
    ]

    power_interval = aggregate_measurements_for_interval(
        asset_id=1,
        interval_start=interval_start,
        interval_end=interval_end,
        measurements=power_measurements,
    )

    assert power_interval.avg_active_power_kw == pytest.approx(50_000.0)
    assert power_interval.energy_kwh == pytest.approx(12_500.0)
    assert power_interval.coverage_ratio == pytest.approx(1.0)
    assert power_interval.quality_status == "valid"


@pytest.mark.aggregation
def test_rejects_duplicate_measurement_times() -> None:
    """Raises ValueError when multiple measurements have the same timestamp."""

    duplicate_time = datetime(2026, 7, 22, 10, 5)

    power_measurements = [
        create_power_measurement(duplicate_time, 40_000.0),
        create_power_measurement(duplicate_time, 60_000.0),
    ]

    with pytest.raises(ValueError, match="Duplicate measurement times"):
        aggregate_measurements_for_interval(
            asset_id=1,
            interval_start=datetime(2026, 7, 22, 10, 0),
            interval_end=datetime(2026, 7, 22, 10, 15),
            measurements=power_measurements,
        )


@pytest.mark.aggregation
def test_rejects_measurement_with_different_asset_id() -> None:
    """Raises ValueError when a measurement belongs to another asset."""

    interval_start = datetime(2026, 7, 22, 10, 0)
    interval_end = datetime(2026, 7, 22, 10, 15)

    power_measurements = [
        create_power_measurement(interval_start, 40_000.0),
        create_power_measurement(interval_end, 60_000.0, asset_id=2),
    ]

    with pytest.raises(ValueError, match="does not match the provided asset_id"):
        aggregate_measurements_for_interval(
            asset_id=1,
            interval_start=interval_start,
            interval_end=interval_end,
            measurements=power_measurements,
        )


@pytest.mark.aggregation
def test_ignores_invalid_measurements() -> None:
    """Excludes invalid measurements from interval aggregation."""

    interval_start = datetime(2026, 7, 22, 10, 0)
    interval_end = datetime(2026, 7, 22, 10, 15)

    power_measurements = [
        create_power_measurement(interval_start, 40_000.0),
        create_power_measurement(
            datetime(2026, 7, 22, 10, 5),
            1_000_000.0,
            quality_status="invalid",
        ),
        create_power_measurement(interval_end, 60_000.0),
    ]

    power_interval = aggregate_measurements_for_interval(
        asset_id=1,
        interval_start=interval_start,
        interval_end=interval_end,
        measurements=power_measurements,
    )

    assert power_interval.avg_active_power_kw == pytest.approx(50_000.0)
    assert power_interval.energy_kwh == pytest.approx(12_500.0)
    assert power_interval.coverage_ratio == pytest.approx(1.0)
    assert power_interval.quality_status == "valid"
    assert power_interval.source_measurement_count == 3
    assert power_interval.valid_measurement_count == 2


@pytest.mark.aggregation
def test_rejects_interval_with_end_before_start() -> None:
    """Raises ValueError when the interval end is not after its start."""

    interval_start = datetime(2026, 7, 22, 10, 15)
    interval_end = datetime(2026, 7, 22, 10, 0)

    power_measurements = [
        create_power_measurement(interval_end, 40_000.0),
        create_power_measurement(interval_start, 60_000.0),
    ]

    with pytest.raises(
        ValueError,
        match="Interval end time must be after interval start time",
    ):
        aggregate_measurements_for_interval(
            asset_id=1,
            interval_start=interval_start,
            interval_end=interval_end,
            measurements=power_measurements,
        )


@pytest.mark.aggregation
def test_rejects_fewer_than_two_measurements() -> None:
    """Raises ValueError when fewer than two measurements are provided."""

    with pytest.raises(ValueError, match="At least two measurements are required"):
        aggregate_measurements_for_interval(
            asset_id=1,
            interval_start=datetime(2026, 7, 22, 10, 0),
            interval_end=datetime(2026, 7, 22, 10, 15),
            measurements=[
                create_power_measurement(datetime(2026, 7, 22, 10, 0), 40_000.0),
            ],
        )


@pytest.mark.aggregation
@pytest.mark.parametrize(
    ("coverage_ratio", "expected_quality_status"),
    [
        (0.0, "invalid"),
        (0.25, "incomplete"),
        (0.5, "incomplete"),
        (0.99, "incomplete"),
        (1.0, "valid"),
    ],
)
def test_determines_quality_status(
    coverage_ratio: float,
    expected_quality_status: str,
) -> None:
    """Maps interval coverage to the expected quality status."""

    quality_status = determine_quality_status(coverage_ratio)

    assert quality_status == expected_quality_status


# ============================================================
# Helper Functions
# ============================================================


@pytest.mark.aggregation
def test_interpolates_support_point_at_midpoint() -> None:
    """Interpolates power linearly between two measurements."""

    left_measurement = create_power_measurement(
        datetime(2026, 7, 22, 10, 0),
        40_000.0,
    )
    right_measurement = create_power_measurement(
        datetime(2026, 7, 22, 10, 10),
        60_000.0,
    )

    support_point = create_interpolated_support_point(
        left_measurement=left_measurement,
        right_measurement=right_measurement,
        target_time=datetime(2026, 7, 22, 10, 5),
    )

    assert support_point.timestamp == datetime(2026, 7, 22, 10, 5)
    assert support_point.active_power_kw == pytest.approx(50_000.0)
    assert support_point.point_type == "interpolated"
    assert support_point.is_interpolated is True


@pytest.mark.aggregation
def test_rejects_interpolation_with_invalid_measurement_order() -> None:
    """Raises ValueError when the right measurement is not later."""

    left_measurement = create_power_measurement(
        datetime(2026, 7, 22, 10, 10),
        60_000.0,
    )
    right_measurement = create_power_measurement(
        datetime(2026, 7, 22, 10, 0),
        40_000.0,
    )

    with pytest.raises(ValueError, match="Right measurement must be later"):
        create_interpolated_support_point(
            left_measurement=left_measurement,
            right_measurement=right_measurement,
            target_time=datetime(2026, 7, 22, 10, 5),
        )


@pytest.mark.aggregation
def test_rejects_interpolation_outside_measurement_range() -> None:
    """Raises ValueError when the target is outside the measurement range."""

    left_measurement = create_power_measurement(
        datetime(2026, 7, 22, 10, 0),
        40_000.0,
    )
    right_measurement = create_power_measurement(
        datetime(2026, 7, 22, 10, 10),
        60_000.0,
    )

    with pytest.raises(ValueError, match="Target time must lie between"):
        create_interpolated_support_point(
            left_measurement=left_measurement,
            right_measurement=right_measurement,
            target_time=datetime(2026, 7, 22, 10, 15),
        )


@pytest.mark.aggregation
def test_calculates_segment_energy_with_trapezoidal_rule() -> None:
    """Calculates segment energy using average boundary power."""

    segment = PowerSegment(
        start_point=PowerSupportPoint(
            timestamp=datetime(2026, 7, 22, 10, 0),
            active_power_kw=40_000.0,
            point_type="measured",
        ),
        end_point=PowerSupportPoint(
            timestamp=datetime(2026, 7, 22, 10, 15),
            active_power_kw=60_000.0,
            point_type="measured",
        ),
    )

    energy_kwh = calculate_segment_energy_kwh(segment)

    assert energy_kwh == pytest.approx(12_500.0)


@pytest.mark.aggregation
def test_builds_segments_between_adjacent_points() -> None:
    """Builds one segment between every pair of adjacent points."""

    calculation_points = [
        PowerSupportPoint(
            timestamp=datetime(2026, 7, 22, 10, 0),
            active_power_kw=40_000.0,
            point_type="measured",
        ),
        PowerSupportPoint(
            timestamp=datetime(2026, 7, 22, 10, 5),
            active_power_kw=50_000.0,
            point_type="measured",
        ),
        PowerSupportPoint(
            timestamp=datetime(2026, 7, 22, 10, 15),
            active_power_kw=60_000.0,
            point_type="measured",
        ),
    ]

    segments = build_segments(calculation_points)

    assert len(segments) == 2
    assert segments[0].start_point == calculation_points[0]
    assert segments[0].end_point == calculation_points[1]
    assert segments[1].start_point == calculation_points[1]
    assert segments[1].end_point == calculation_points[2]
