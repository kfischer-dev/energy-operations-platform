import pytest
from src.simulation.profiles import calculate_daylight_factor, calculate_solar_power_kw

@pytest.mark.sim_profiles
def test_daylight_factor_before_sunrise(daylight_factor_payload):
   
    # Current time 05:00 AM in minutes
    time_minutes = 300
    sunrise_minutes, peak_minutes, sunset_minutes = daylight_factor_payload
    daylight_factor = calculate_daylight_factor(time_minutes, sunrise_minutes, peak_minutes, sunset_minutes)

    assert daylight_factor == 0

@pytest.mark.sim_profiles
def test_daylight_factor_at_sunrise(daylight_factor_payload):
    # Current time 06:30 AM in minutes
    time_minutes = 390
    sunrise_minutes, peak_minutes, sunset_minutes = daylight_factor_payload
    daylight_factor = calculate_daylight_factor(time_minutes, sunrise_minutes, peak_minutes, sunset_minutes)

    assert daylight_factor == 0

@pytest.mark.sim_profiles
def test_daylight_factor_between_sunrise_and_peak(daylight_factor_payload):
    # Current time 10:00 AM in minutes
    time_minutes = 600
    sunrise_minutes, peak_minutes, sunset_minutes = daylight_factor_payload
    daylight_factor = calculate_daylight_factor(time_minutes, sunrise_minutes, peak_minutes, sunset_minutes)

    assert daylight_factor == pytest.approx(0.583, abs=0.001)

@pytest.mark.sim_profiles
def test_daylight_factor_at_peak(daylight_factor_payload):
    # Current time 12:30 PM in minutes
    time_minutes = 750
    sunrise_minutes, peak_minutes, sunset_minutes = daylight_factor_payload
    daylight_factor = calculate_daylight_factor(time_minutes, sunrise_minutes, peak_minutes, sunset_minutes)

    assert daylight_factor == 1

@pytest.mark.sim_profiles
def test_daylight_factor_between_peak_and_sunset(daylight_factor_payload):
    # Current time 4:00 PM in minutes
    time_minutes = 960
    sunrise_minutes, peak_minutes, sunset_minutes = daylight_factor_payload
    daylight_factor = calculate_daylight_factor(time_minutes, sunrise_minutes, peak_minutes, sunset_minutes)

    assert daylight_factor == pytest.approx(0.417, abs=0.001)

@pytest.mark.sim_profiles
def test_daylight_factor_at_sunset(daylight_factor_payload):
    # Current time 06:30 PM in minutes
    time_minutes = 1110
    sunrise_minutes, peak_minutes, sunset_minutes = daylight_factor_payload
    daylight_factor = calculate_daylight_factor(time_minutes, sunrise_minutes, peak_minutes, sunset_minutes)

    assert daylight_factor == 0

@pytest.mark.sim_profiles
def test_daylight_factor_after_sunset(daylight_factor_payload):
    # Current time 10:00 PM in minutes
    time_minutes = 1320
    sunrise_minutes, peak_minutes, sunset_minutes = daylight_factor_payload
    daylight_factor = calculate_daylight_factor(time_minutes, sunrise_minutes, peak_minutes, sunset_minutes)

    assert daylight_factor == 0

@pytest.mark.sim_profiles
def test_double_rated_power_results_in_double_solar_power(daylight_factor_payload):
    rated_power_kw = 80000
    rated_power_kw_doubled = 160000

    time_minutes = 600 # Current time 10:00 AM in minutes
    sunrise_minutes, peak_minutes, sunset_minutes = daylight_factor_payload

    active_power_kw = calculate_solar_power_kw(rated_power_kw, time_minutes, sunrise_minutes, peak_minutes, sunset_minutes)
    active_power_kw_doubled = calculate_solar_power_kw(rated_power_kw_doubled, time_minutes, sunrise_minutes, peak_minutes, sunset_minutes)

    assert active_power_kw <= rated_power_kw
    assert active_power_kw_doubled == pytest.approx(active_power_kw * 2)

@pytest.mark.sim_profiles
def test_solar_power_never_exceeds_rated_power(daylight_factor_payload):
    rated_power_kw = 80_000
    sunrise_minutes, peak_minutes, sunset_minutes = daylight_factor_payload

    for time_minutes in range(24 * 60):
        active_power_kw = calculate_solar_power_kw(rated_power_kw, time_minutes, sunrise_minutes, peak_minutes, sunset_minutes,)

        assert 0 <= active_power_kw <= rated_power_kw

@pytest.mark.sim_profiles
@pytest.mark.parametrize(
    "sunrise_minutes, peak_minutes, sunset_minutes",
    [
        (750, 1110, 390),
        (750, 390, 1110),
        (1110, 750, 390),
        (1110, 390, 750),
        (390, 1110, 750),
        (390, 390, 1110),
        (390, 1110, 1110),
        (390, 390, 390),
    ],
)
def test_invalid_sequence_of_sun_times(sunrise_minutes, peak_minutes, sunset_minutes):
    time_minutes = 960

    with pytest.raises(ValueError, match="Sequence of sun times is wrong!"):
        calculate_daylight_factor(time_minutes, sunrise_minutes, peak_minutes, sunset_minutes)


