from datetime import datetime
from unittest.mock import ANY, MagicMock

import pytest

from src.measurements.models import PowerMeasurement
from src.simulation.repository import insert_power_measurements

SIMULATION_RUN_ID = 42


def expected_measurement_row(
    measurement: PowerMeasurement,
) -> tuple[int, int, datetime, float, str, str]:
    """Return the database values expected for one power measurement."""

    return (
        measurement.asset_id,
        SIMULATION_RUN_ID,
        measurement.measurement_time,
        measurement.active_power_kw,
        measurement.source,
        measurement.quality_status,
    )


@pytest.mark.repository
def test_insert_power_measurements_uses_point_measurement_values() -> None:
    """Persist exact power timestamps without interval or energy fields."""

    connection = MagicMock()
    cursor = connection.cursor.return_value.__enter__.return_value
    measurements = [
        PowerMeasurement(
            asset_id=1,
            measurement_time=datetime(2026, 7, 28, 10, 0),
            active_power_kw=120_000.0,
            source="simulation",
            quality_status="valid",
        )
    ]

    inserted_count = insert_power_measurements(
        connection,
        measurements,
        simulation_run_id=SIMULATION_RUN_ID,
    )

    cursor.executemany.assert_called_once_with(
        ANY,
        [expected_measurement_row(measurements[0])],
    )
    assert inserted_count == 1


@pytest.mark.repository
def test_insert_power_measurements_inserts_multiple_rows() -> None:
    """Persist multiple point-in-time power measurements in one batch."""

    connection = MagicMock()
    cursor = connection.cursor.return_value.__enter__.return_value

    measurements = [
        PowerMeasurement(
            asset_id=1,
            measurement_time=datetime(2026, 7, 28, 10, 0),
            active_power_kw=120_000.0,
            source="simulation",
            quality_status="valid",
        ),
        PowerMeasurement(
            asset_id=1,
            measurement_time=datetime(2026, 7, 28, 10, 15),
            active_power_kw=125_000.0,
            source="simulation",
            quality_status="valid",
        ),
        PowerMeasurement(
            asset_id=2,
            measurement_time=datetime(2026, 7, 28, 10, 0),
            active_power_kw=80_000.0,
            source="simulation",
            quality_status="valid",
        ),
    ]

    inserted_count = insert_power_measurements(
        connection,
        measurements,
        simulation_run_id=SIMULATION_RUN_ID,
    )

    cursor.executemany.assert_called_once_with(
        ANY,
        [expected_measurement_row(measurement) for measurement in measurements],
    )

    assert inserted_count == 3


@pytest.mark.repository
def test_insert_power_measurements_returns_zero_for_empty_list() -> None:
    """Skip database access when no measurements are available."""

    connection = MagicMock()

    inserted_count = insert_power_measurements(
        connection,
        [],
        simulation_run_id=SIMULATION_RUN_ID,
    )

    assert inserted_count == 0
    connection.cursor.assert_not_called()
