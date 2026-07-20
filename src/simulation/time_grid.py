from datetime import datetime, timedelta


def generate_time_grid(
    start_time: datetime,
    end_time: datetime,
    interval_minutes: int,
) -> list[datetime]:
    """Generate timestamps for all complete intervals in a time range."""

    duration_minutes = (end_time - start_time).total_seconds() / 60

    if end_time <= start_time:
        raise ValueError(
            "No time grid calculation possible. "
            f"End time '{end_time}' must be after start time '{start_time}'."
        )

    if interval_minutes <= 0:
        raise ValueError("interval_minutes must be positive")

    if interval_minutes > duration_minutes:
        raise ValueError(
            "Simulation time should be bigger than the interval"
        )

    total_intervals = int(duration_minutes // interval_minutes)
    effective_end_time = start_time + timedelta(
        minutes=total_intervals * interval_minutes
    )

    time_grid: list[datetime] = []
    current_time = start_time

    while current_time <= effective_end_time:
        time_grid.append(current_time)
        current_time += timedelta(minutes=interval_minutes)

    return time_grid
