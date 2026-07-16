from datetime import time

# Profile Solar

def calculate_daylight_factor(time_minutes: int, sunrise_minutes: int, peak_minutes: int, sunset_minutes: int) -> float:

    if not sunrise_minutes < peak_minutes < sunset_minutes:
        raise ValueError("Sequence of sun times is wrong!")

    # Before peak
    if sunrise_minutes <= time_minutes <= peak_minutes:
        daylight_factor =  (time_minutes - sunrise_minutes) / (peak_minutes - sunrise_minutes)
    # After Peak
    elif peak_minutes <= time_minutes <= sunset_minutes:
        daylight_factor = (sunset_minutes - time_minutes) / (sunset_minutes - peak_minutes)
    # At night
    else:
        daylight_factor = 0.0
    
    return daylight_factor

def calculate_solar_power_kw(rated_power_kw: float, time_minutes: int, sunrise_minutes: int, peak_minutes: int, sunset_minutes: int,) -> float:
    daylight_factor = calculate_daylight_factor(time_minutes, sunrise_minutes, peak_minutes, sunset_minutes)
    return rated_power_kw * daylight_factor

def time_to_minutes(value: time) -> int:
    return value.hour * 60 + value.minute
