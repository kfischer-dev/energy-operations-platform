import pytest
from src.simulation.time_grid import generate_time_grid
from datetime import datetime

@pytest.mark.simulation
def test_valid_standard_time_grid():
    start_time = datetime(2026, 7, 15, 10, 0, 0)
    end_time =  datetime(2026, 7, 15, 12, 0, 0)
    interval_minutes = 15
    time_grid = generate_time_grid(start_time, end_time, interval_minutes)

    assert len(time_grid) == 9
    assert time_grid[0] == datetime(2026, 7, 15, 10, 0)
    assert time_grid[-1] == datetime(2026, 7, 15, 12, 0)

@pytest.mark.simulation
def test_valid_24h_time_grid():
    start_time = datetime(2026, 7, 15, 0, 0, 0)
    end_time =  datetime(2026, 7, 16, 0, 0, 0)
    interval_minutes = 15

    time_grid = generate_time_grid(start_time, end_time, interval_minutes)

    assert len(time_grid) == 97
    assert time_grid[0] == datetime(2026, 7, 15, 0, 0)
    assert time_grid[-1] == datetime(2026, 7, 16, 0, 0)

@pytest.mark.simulation
def test_invalid_time_period():
    start_time = datetime(2026, 7, 15, 10, 0, 0)
    end_time =  datetime(2026, 7, 15, 8, 0, 0)
    interval_minutes = 15
    with pytest.raises(ValueError, match="No time grid calculation possible"):
        generate_time_grid(start_time, end_time, interval_minutes)

@pytest.mark.simulation
def test_invalid_interval():
    start_time = datetime(2026, 7, 15, 10, 0, 0)
    end_time =  datetime(2026, 7, 15, 12, 0, 0)
    interval_minutes = 0
    with pytest.raises(ValueError, match="interval_minutes must be positive"):
        generate_time_grid(start_time, end_time, interval_minutes)

@pytest.mark.simulation
def test_invalid_simulation_time():
    start_time = datetime(2026, 7, 15, 10, 0, 0)
    end_time =  datetime(2026, 7, 15, 10, 10, 0)
    interval_minutes = 15
    with pytest.raises(ValueError, match="Simulation time should be bigger than the interval"):
        generate_time_grid(start_time, end_time, interval_minutes)

@pytest.mark.simulation
def test_time_grid_ignores_incomplete_final_interval():
    start_time = datetime(2026, 7, 15, 10, 0, 0)
    end_time =  datetime(2026, 7, 15, 12, 12, 0)
    interval_minutes = 15
    time_grid = generate_time_grid(start_time, end_time, interval_minutes)

    assert len(time_grid) == 9
    assert time_grid[0] == datetime(2026, 7, 15, 10, 0)
    assert time_grid[-1] == datetime(2026, 7, 15, 12, 0)

