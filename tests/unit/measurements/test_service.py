from datetime import datetime

import pytest

from src.measurements.service import calculate_asset_kpis, calculate_kpis_for_all_measurements


@pytest.mark.basic
def test_calculate_asset_kpis_returns_empty_kpis_without_measurements():
    """Return empty period KPIs when no measurements are available."""

    start_time = datetime.fromisoformat("2026-06-22T08:00:00+02:00")
    end_time = datetime.fromisoformat("2026-06-22T08:30:00+02:00")

    kpis = calculate_asset_kpis(
        measurements=[],
        asset_id=1,
        start_time=start_time,
        end_time=end_time,
    )

    assert kpis["period_start"] == start_time
    assert kpis["period_end"] == end_time

    assert kpis["measurement_count"] == 0
    assert kpis["min_measured_power_kw"] is None
    assert kpis["max_measured_power_kw"] is None

    assert kpis["avg_active_power_kw"] is None
    assert kpis["total_energy_kwh"] is None
    assert kpis["coverage_ratio"] == 0.0


@pytest.mark.basic
def test_calculate_asset_kpis_returns_measurement_kpis_for_single_measurement():
    """Keep measured KPIs but skip interval KPIs for one measurement."""

    start_time = datetime.fromisoformat("2026-06-22T08:00:00+02:00")
    end_time = datetime.fromisoformat("2026-06-22T08:30:00+02:00")

    measurements = [
        {
            "asset_id": 5,
            "measurement_time": datetime.fromisoformat("2026-06-22T08:30:00+02:00"),
            "active_power_kw": 102000.0,
            "source": "simulation",
            "quality_status": "valid",
        }
    ]

    kpis = calculate_asset_kpis(
        measurements=measurements,
        asset_id=5,
        start_time=start_time,
        end_time=end_time,
    )

    assert kpis["period_start"] == start_time
    assert kpis["period_end"] == end_time

    assert kpis["measurement_count"] == 1
    assert kpis["min_measured_power_kw"] == 102000.0
    assert kpis["max_measured_power_kw"] == 102000.0

    assert kpis["avg_active_power_kw"] is None
    assert kpis["total_energy_kwh"] is None
    assert kpis["coverage_ratio"] == 0.0


@pytest.mark.basic
def test_calculate_asset_kpis_aggregates_when_two_measurements_are_available():
    """Calculate interval KPIs when at least two measurements are available."""

    start_time = datetime.fromisoformat("2026-06-22T08:00:00+02:00")
    end_time = datetime.fromisoformat("2026-06-22T08:30:00+02:00")

    measurements = [
        {
            "asset_id": 1,
            "measurement_time": start_time,
            "active_power_kw": 100.0,
            "source": "simulation",
            "quality_status": "valid",
        },
        {
            "asset_id": 1,
            "measurement_time": end_time,
            "active_power_kw": 100.0,
            "source": "simulation",
            "quality_status": "valid",
        },
    ]

    kpis = calculate_asset_kpis(
        measurements=measurements,
        asset_id=1,
        start_time=start_time,
        end_time=end_time,
    )

    assert kpis["measurement_count"] == 2
    assert kpis["min_measured_power_kw"] == 100.0
    assert kpis["max_measured_power_kw"] == 100.0

    assert kpis["avg_active_power_kw"] == 100.0
    assert kpis["total_energy_kwh"] == 50.0
    assert kpis["coverage_ratio"] == 1.0


@pytest.mark.basic
def test_calculate_kpis_for_all_measurements_returns_empty_kpis_without_measurements():
    start_time = datetime.fromisoformat("2026-06-22T08:00:00+02:00")
    end_time = datetime.fromisoformat("2026-06-22T08:30:00+02:00")

    result = calculate_kpis_for_all_measurements(
        measurements=[],
        start_time=start_time,
        end_time=end_time,
    )

    assert result["period_start"] == start_time
    assert result["period_end"] == end_time
    assert result["measurement_count"] == 0
    assert result["min_measured_power_kw"] is None
    assert result["max_measured_power_kw"] is None
    assert result["avg_active_power_kw"] is None
    assert result["total_energy_kwh"] is None
    assert result["coverage_ratio"] == pytest.approx(0.0)


@pytest.mark.basic
def test_calculate_kpis_for_all_measurements_returns_none_when_no_asset_is_aggregatable():
    """Return no period KPIs when measurements exist but no time series is aggregatable."""

    start_time = datetime.fromisoformat("2026-06-22T08:00:00+02:00")
    end_time = datetime.fromisoformat("2026-06-22T08:30:00+02:00")

    measurements = [
        {
            "asset_id": 1,
            "measurement_time": datetime.fromisoformat(
                "2026-06-22T08:15:00+02:00"
            ),
            "active_power_kw": 100.0,
            "source": "simulation",
            "quality_status": "valid",
        },
        {
            "asset_id": 2,
            "measurement_time": datetime.fromisoformat(
                "2026-06-22T08:15:00+02:00"
            ),
            "active_power_kw": 200.0,
            "source": "simulation",
            "quality_status": "valid",
        },
    ]

    result = calculate_kpis_for_all_measurements(
        measurements=measurements,
        start_time=start_time,
        end_time=end_time,
    )

    assert result["period_start"] == start_time
    assert result["period_end"] == end_time

    assert result["measurement_count"] == 2
    assert result["min_measured_power_kw"] == 100.0
    assert result["max_measured_power_kw"] == 200.0

    assert result["avg_active_power_kw"] is None
    assert result["total_energy_kwh"] is None
    assert result["coverage_ratio"] == pytest.approx(0.0)