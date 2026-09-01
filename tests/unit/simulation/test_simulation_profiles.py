from dataclasses import replace
from datetime import datetime
from random import Random

import pytest

from src.simulation import default_data
from src.simulation.profiles import (
    CITY_LOAD_PROFILE,
    INDUSTRIAL_LOAD_PROFILE,
    calculate_city_load_kw,
    calculate_daylight_factor,
    calculate_industrial_load_kw,
    calculate_load_factor,
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


@pytest.mark.sim_profiles
def test_calculate_load_factor():

    time_minutes = (300, 360, 420, 1200)  # 5:00 AM, 6:00 AM, 7:00 AM, 8:00 PM

    city_load_factor = []

    for i in range(len(time_minutes)):
        city_load_factor.append(
            calculate_load_factor(
                profile=CITY_LOAD_PROFILE,
                time_minutes=time_minutes[i],
            )
        )

    assert city_load_factor[0] == pytest.approx(0.28)
    assert city_load_factor[1] == pytest.approx(0.415)
    assert city_load_factor[2] == pytest.approx(0.55)
    assert city_load_factor[3] == pytest.approx(0.9)

    industrial_load_factor = []

    for i in range(len(time_minutes)):
        industrial_load_factor.append(
            calculate_load_factor(
                profile=INDUSTRIAL_LOAD_PROFILE,
                time_minutes=time_minutes[i],
            )
        )

    assert industrial_load_factor[0] == pytest.approx(0.25)
    assert industrial_load_factor[1] == pytest.approx(0.4)
    assert industrial_load_factor[2] == pytest.approx(0.625)
    assert industrial_load_factor[3] == pytest.approx(0.365)


@pytest.mark.sim_profiles
def test_calculate_city_and_industrial_load():

    config = default_data.create_default_simulation_config()
    random_generator = Random(config.random_seed)

    city_asset = default_data.create_default_city_load_asset()
    industrial_asset = default_data.create_default_industrial_load_asset()

    city_context_1 = default_data.create_default_city_load_context(
        config=config,
        current_time=datetime(2026, 9, 1, 10, 0),
        random_generator=random_generator,
    )
    city_context_2 = replace(
        default_data.create_default_city_load_context(
            config=config,
            current_time=datetime(2026, 9, 1, 10, 0),
            random_generator=random_generator,
        ),
        load_factor=0.5,
    )
    industrial_context_1 = default_data.create_default_industrial_load_context(
        config=config,
        current_time=datetime(2026, 9, 1, 10, 0),
        random_generator=random_generator,
    )
    industrial_context_2 = replace(
        default_data.create_default_industrial_load_context(
            config=config,
            current_time=datetime(2026, 9, 1, 10, 0),
            random_generator=random_generator,
        ),
        load_factor=0.5,
    )

    city_load_1 = calculate_city_load_kw(
        asset=city_asset,
        context=city_context_1,
        profile_data={},
    )

    city_load_2 = calculate_city_load_kw(
        asset=city_asset,
        context=city_context_2,
        profile_data={},
    )

    industrial_load_1 = calculate_industrial_load_kw(
        asset=industrial_asset,
        context=industrial_context_1,
        profile_data={},
    )

    industrial_load_2 = calculate_industrial_load_kw(
        asset=industrial_asset,
        context=industrial_context_2,
        profile_data={},
    )

    assert city_load_2 == pytest.approx(city_load_1 * city_context_2.load_factor)

    assert industrial_load_2 == pytest.approx(
        industrial_load_1 * industrial_context_2.load_factor
    )
