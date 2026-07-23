from datetime import datetime

import pytest

from src.simulation.time_grid import generate_time_grid


@pytest.mark.time_grid
@pytest.mark.parametrize(
    ("start_time", "end_time", "expected_count"),
    [
        (
            datetime(2026, 7, 15, 10, 0),
            datetime(2026, 7, 15, 12, 0),
            9,
        ),
        (
            datetime(2026, 7, 15, 0, 0),
            datetime(2026, 7, 16, 0, 0),
            97,
        ),
    ],
)
def test_valid_time_grid_contains_expected_grid_points(
    start_time,
    end_time,
    expected_count,
):
    time_grid = generate_time_grid(
        start_time,
        end_time,
        interval_minutes=15,
    )

    assert len(time_grid) == expected_count
    assert time_grid[0] == start_time
    assert time_grid[-1] == end_time


@pytest.mark.time_grid
def test_end_time_before_start_time_raises_value_error():
    with pytest.raises(
        ValueError,
        match="No time grid calculation possible",
    ):
        generate_time_grid(
            start_time=datetime(2026, 7, 15, 10, 0),
            end_time=datetime(2026, 7, 15, 8, 0),
            interval_minutes=15,
        )


@pytest.mark.time_grid
def test_non_positive_interval_raises_value_error():
    with pytest.raises(
        ValueError,
        match="interval_minutes must be positive",
    ):
        generate_time_grid(
            start_time=datetime(2026, 7, 15, 10, 0),
            end_time=datetime(2026, 7, 15, 12, 0),
            interval_minutes=0,
        )


@pytest.mark.time_grid
def test_interval_longer_than_simulation_raises_value_error():
    with pytest.raises(
        ValueError,
        match="Simulation time should be bigger than the interval",
    ):
        generate_time_grid(
            start_time=datetime(2026, 7, 15, 10, 0),
            end_time=datetime(2026, 7, 15, 10, 10),
            interval_minutes=15,
        )


@pytest.mark.time_grid
def test_time_grid_ignores_incomplete_final_interval():
    start_time = datetime(2026, 7, 15, 10, 0)
    requested_end_time = datetime(2026, 7, 15, 12, 12)
    expected_effective_end_time = datetime(2026, 7, 15, 12, 0)

    time_grid = generate_time_grid(
        start_time,
        requested_end_time,
        interval_minutes=15,
    )

    assert len(time_grid) == 9
    assert time_grid[0] == start_time
    assert time_grid[-1] == expected_effective_end_time
