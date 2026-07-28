from datetime import datetime
from unittest.mock import ANY, MagicMock

import pytest

from src.measurements.models import PowerMeasurement
from src.simulation.repository import insert_power_measurements


SIMULATION_RUN_ID = 42


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
        [
            (
                measurements[0].asset_id,
                SIMULATION_RUN_ID,
                measurements[0].measurement_time,
                measurements[0].active_power_kw,
                measurements[0].source,
                measurements[0].quality_status,
            )
        ],
    )
    assert inserted_count == 1
