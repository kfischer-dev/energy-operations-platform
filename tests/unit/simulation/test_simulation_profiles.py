from dataclasses import replace
from datetime import datetime
from random import Random

import pytest

from src.simulation import default_data
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
    """Verify that solar output scales linearly with rated power."""

    config = default_data.create_default_simulation_config()
    asset = replace(
        default_data.create_default_solar_asset(),
        rated_power_kw=80_000,
    )
    doubled_asset = replace(
        asset,
        rated_power_kw=160_000,
    )
    context = default_data.create_default_solar_context(
        config=config,
        current_time=datetime(2026, 7, 16, 10, 0),
        random_generator=Random(config.random_seed),
    )

    sunrise_minutes, peak_minutes, sunset_minutes = daylight_factor_payload
    profile_data = {
        "solar_park": {
            "sunrise_minutes": sunrise_minutes,
            "peak_minutes": peak_minutes,
            "sunset_minutes": sunset_minutes,
        }
    }

    active_power_kw = calculate_solar_power_kw(
        asset,
        context,
        profile_data,
    )
    doubled_active_power_kw = calculate_solar_power_kw(
        doubled_asset,
        context,
        profile_data,
    )

    assert active_power_kw <= asset.rated_power_kw
    assert doubled_active_power_kw == pytest.approx(active_power_kw * 2)


@pytest.mark.sim_profiles
def test_solar_power_never_exceeds_rated_power(daylight_factor_payload):
    """Verify that the solar profile stays within valid power limits."""

    config = default_data.create_default_simulation_config()
    asset = replace(
        default_data.create_default_solar_asset(),
        rated_power_kw=80_000,
    )
    random_generator = Random(config.random_seed)

    sunrise_minutes, peak_minutes, sunset_minutes = daylight_factor_payload
    profile_data = {
        "solar_park": {
            "sunrise_minutes": sunrise_minutes,
            "peak_minutes": peak_minutes,
            "sunset_minutes": sunset_minutes,
        }
    }

    for time_minutes in range(24 * 60):
        hour, minute = divmod(time_minutes, 60)
        context = default_data.create_default_solar_context(
            config=config,
            current_time=datetime(2026, 7, 16, hour, minute),
            random_generator=random_generator,
        )

        active_power_kw = calculate_solar_power_kw(
            asset,
            context,
            profile_data,
        )

        assert 0 <= active_power_kw <= asset.rated_power_kw


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
    """Reject invalid chronological sequences of solar profile times."""

    with pytest.raises(ValueError, match="Sequence of sun times is wrong!"):
        calculate_daylight_factor(
            time_minutes=960,
            sunrise_minutes=sunrise_minutes,
            peak_minutes=peak_minutes,
            sunset_minutes=sunset_minutes,
        )
