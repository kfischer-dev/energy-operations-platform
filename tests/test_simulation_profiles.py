import pytest

from src.simulation.profiles import (
    calculate_daylight_factor,
    calculate_solar_power_kw,
)


@pytest.mark.sim_profiles
@pytest.mark.parametrize(
    ("time_minutes", "expected_factor"),
    [
        pytest.param(300, 0.0, id="before-sunrise"),
        pytest.param(390, 0.0, id="at-sunrise"),
        pytest.param(600, 0.583, id="between-sunrise-and-peak"),
        pytest.param(750, 1.0, id="at-peak"),
        pytest.param(960, 0.417, id="between-peak-and-sunset"),
        pytest.param(1110, 0.0, id="at-sunset"),
        pytest.param(1320, 0.0, id="after-sunset"),
    ],
)
def test_daylight_factor_at_representative_times(
    daylight_factor_payload,
    time_minutes,
    expected_factor,
):
    """Verify the solar profile before, during and after daylight."""

    sunrise_minutes, peak_minutes, sunset_minutes = daylight_factor_payload

    daylight_factor = calculate_daylight_factor(
        time_minutes,
        sunrise_minutes,
        peak_minutes,
        sunset_minutes,
    )

    assert daylight_factor == pytest.approx(expected_factor, abs=0.001)


@pytest.mark.sim_profiles
def test_double_rated_power_results_in_double_solar_power(
    daylight_factor_payload,
):
    rated_power_kw = 80_000
    doubled_rated_power_kw = 160_000
    time_minutes = 600

    sunrise_minutes, peak_minutes, sunset_minutes = daylight_factor_payload

    active_power_kw = calculate_solar_power_kw(
        rated_power_kw,
        time_minutes,
        sunrise_minutes,
        peak_minutes,
        sunset_minutes,
    )
    doubled_active_power_kw = calculate_solar_power_kw(
        doubled_rated_power_kw,
        time_minutes,
        sunrise_minutes,
        peak_minutes,
        sunset_minutes,
    )

    assert active_power_kw <= rated_power_kw
    assert doubled_active_power_kw == pytest.approx(active_power_kw * 2)


@pytest.mark.sim_profiles
def test_solar_power_never_exceeds_rated_power(daylight_factor_payload):
    rated_power_kw = 80_000
    sunrise_minutes, peak_minutes, sunset_minutes = daylight_factor_payload

    for time_minutes in range(24 * 60):
        active_power_kw = calculate_solar_power_kw(
            rated_power_kw,
            time_minutes,
            sunrise_minutes,
            peak_minutes,
            sunset_minutes,
        )

        assert 0 <= active_power_kw <= rated_power_kw


@pytest.mark.sim_profiles
@pytest.mark.parametrize(
    ("sunrise_minutes", "peak_minutes", "sunset_minutes"),
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
def test_invalid_sequence_of_sun_times(
    sunrise_minutes,
    peak_minutes,
    sunset_minutes,
):
    with pytest.raises(ValueError, match="Sequence of sun times is wrong!"):
        calculate_daylight_factor(
            time_minutes=960,
            sunrise_minutes=sunrise_minutes,
            peak_minutes=peak_minutes,
            sunset_minutes=sunset_minutes,
        )
