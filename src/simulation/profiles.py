from datetime import time


def calculate_daylight_factor(
    time_minutes: int,
    sunrise_minutes: int,
    peak_minutes: int,
    sunset_minutes: int,
) -> float:
    """Calculate a triangular daylight factor between sunrise and sunset."""

    if not sunrise_minutes < peak_minutes < sunset_minutes:
        raise ValueError("Sequence of sun times is wrong!")

    if sunrise_minutes <= time_minutes <= peak_minutes:
        return ( time_minutes - sunrise_minutes ) / ( peak_minutes - sunrise_minutes )

    if peak_minutes <= time_minutes <= sunset_minutes:
        return ( sunset_minutes - time_minutes ) / ( sunset_minutes - peak_minutes )

    return 0.0


def calculate_solar_power_kw(
    rated_power_kw: float,
    time_minutes: int,
    sunrise_minutes: int,
    peak_minutes: int,
    sunset_minutes: int,
) -> float:
    """Calculate solar power from rated power and the daylight factor."""

    daylight_factor = calculate_daylight_factor(
        time_minutes,
        sunrise_minutes,
        peak_minutes,
        sunset_minutes,
    )
    return rated_power_kw * daylight_factor


def time_to_minutes(value: time) -> int:
    """Convert a time value to minutes after midnight."""

    return value.hour * 60 + value.minute
