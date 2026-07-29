from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from src.measurements.models import PowerIntervalDraft, PowerMeasurement
from src.simulation import service as simulation_service
from src.simulation.models import SimulationConfig

SIMULATION_RUN_ID = 42
EXPECTED_COMMIT_COUNT = 3


@pytest.fixture
def simulation_config() -> SimulationConfig:
    """Return a valid configuration for simulation service tests."""

    return SimulationConfig(
        start_time=datetime(2026, 7, 28, 10, 0),
        end_time=datetime(2026, 7, 28, 10, 30),
        interval_minutes=15,
        random_seed=42,
        simulation_mode="historical",
    )


@pytest.fixture
def service_mocks(monkeypatch: pytest.MonkeyPatch) -> SimpleNamespace:
    """Replace external simulation-service operations with named mocks."""

    mocks = SimpleNamespace(
        create_run=MagicMock(return_value=SIMULATION_RUN_ID),
        mark_running=MagicMock(),
        simulate_assets=MagicMock(),
        insert_measurements=MagicMock(),
        aggregate_measurements=MagicMock(),
        validate_intervals=MagicMock(),
        mark_completed=MagicMock(),
        mark_failed=MagicMock(),
    )
    replacements = {
        "create_simulation_run": mocks.create_run,
        "mark_simulation_run_running": mocks.mark_running,
        "simulate_database_assets": mocks.simulate_assets,
        "insert_power_measurements": mocks.insert_measurements,
        "aggregate_simulation_measurements": mocks.aggregate_measurements,
        "validate_simulation_intervals": mocks.validate_intervals,
        "mark_simulation_run_completed": mocks.mark_completed,
        "mark_simulation_run_failed": mocks.mark_failed,
    }

    for name, mock in replacements.items():
        monkeypatch.setattr(simulation_service, name, mock)

    return mocks


@pytest.mark.service
def test_execute_simulation_run_persists_measurements_and_completes_run(
    simulation_config: SimulationConfig,
    service_mocks: SimpleNamespace,
) -> None:
    """Persist generated measurements and complete the simulation run."""

    connection = MagicMock()

    power_measurements = [
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
    ]

    power_intervals = [
        PowerIntervalDraft(
            asset_id=1,
            interval_start=datetime(2026, 7, 28, 10, 0),
            interval_end=datetime(2026, 7, 28, 10, 15),
            avg_active_power_kw=122_500.0,
            energy_kwh=30_625.0,
            quality_status="valid",
            aggregation_method="time_weighted_average",
            source_measurement_count=2,
            valid_measurement_count=2,
            coverage_ratio=1.0,
        )
    ]

    service_mocks.simulate_assets.return_value = power_measurements
    service_mocks.insert_measurements.return_value = 2
    service_mocks.aggregate_measurements.return_value = power_intervals

    result = simulation_service.execute_simulation_run(
        connection,
        simulation_config,
    )

    service_mocks.create_run.assert_called_once_with(
        connection,
        simulation_config,
    )
    service_mocks.mark_running.assert_called_once_with(
        connection,
        SIMULATION_RUN_ID,
    )
    service_mocks.simulate_assets.assert_called_once_with(
        connection,
        simulation_config,
    )
    service_mocks.insert_measurements.assert_called_once_with(
        connection,
        power_measurements,
        SIMULATION_RUN_ID,
    )
    service_mocks.aggregate_measurements.assert_called_once_with(
        power_measurements,
        simulation_config,
    )
    service_mocks.validate_intervals.assert_called_once_with(
        power_intervals,
    )
    service_mocks.mark_completed.assert_called_once_with(
        connection,
        SIMULATION_RUN_ID,
        generated_measurement_count=2,
    )

    assert connection.commit.call_count == EXPECTED_COMMIT_COUNT
    connection.rollback.assert_not_called()
    assert result == power_intervals


@pytest.mark.service
def test_execute_simulation_run_marks_run_failed_when_batch_insert_fails(
    simulation_config: SimulationConfig,
    service_mocks: SimpleNamespace,
) -> None:
    """Rollback persisted changes and mark the run as failed after an insert error."""

    connection = MagicMock()

    power_measurements = [
        PowerMeasurement(
            asset_id=1,
            measurement_time=datetime(2026, 7, 28, 10, 0),
            active_power_kw=120_000.0,
            source="simulation",
            quality_status="valid",
        )
    ]

    service_mocks.simulate_assets.return_value = power_measurements
    service_mocks.insert_measurements.side_effect = RuntimeError("Batch insert failed")

    with pytest.raises(
        RuntimeError,
        match="Batch insert failed",
    ):
        simulation_service.execute_simulation_run(
            connection,
            simulation_config,
        )

    service_mocks.mark_running.assert_called_once_with(
        connection,
        SIMULATION_RUN_ID,
    )
    service_mocks.insert_measurements.assert_called_once_with(
        connection,
        power_measurements,
        SIMULATION_RUN_ID,
    )

    connection.rollback.assert_called_once_with()
    service_mocks.mark_failed.assert_called_once_with(
        connection,
        SIMULATION_RUN_ID,
    )

    assert connection.commit.call_count == EXPECTED_COMMIT_COUNT
