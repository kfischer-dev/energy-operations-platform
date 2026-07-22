from dataclasses import replace
from datetime import datetime
from random import Random

import pytest

from src.simulation.simulation import (
    simulate_asset_power_grid,
    simulate_power_of_asset,
)
from src.simulation.time_grid import generate_time_grid



# ============================================================
# General engine tests
# ============================================================


@pytest.mark.simulation
@pytest.mark.parametrize(
    "engine_payload",
    ["solar_park", "wind_park", "hydro_power_plant", "biomass_power_plant"],
    indirect=True,
)
@pytest.mark.parametrize("operating_status", ["offline", "maintenance", "fault"])
def test_inactive_asset_returns_zero_power(engine_payload, operating_status):
    inactive_asset = replace(
        engine_payload["asset"],
        operating_status=operating_status,
    )

    active_power_kw = simulate_power_of_asset(
        inactive_asset,
        engine_payload["context"],
        engine_payload["profile_data"],
    )

    assert active_power_kw == 0


@pytest.mark.simulation
@pytest.mark.parametrize("engine_payload", ["solar_park"], indirect=True)
def test_unknown_asset_type_raises_not_implemented_error(engine_payload):
    unknown_type_asset = replace(
        engine_payload["asset"],
        asset_type="unknown",
    )

    with pytest.raises(NotImplementedError, match="is not supported yet"):
        simulate_power_of_asset(
            unknown_type_asset,
            engine_payload["context"],
            engine_payload["profile_data"],
        )


# ============================================================
# General simulation tests
# ============================================================


@pytest.mark.simulation
@pytest.mark.parametrize("engine_payload", ["solar_park"], indirect=True)
def test_simulation_generates_expected_number_of_measurements(engine_payload):
    measurements = simulate_asset_power_grid(
        engine_payload["config"],
        engine_payload["asset"],
    )

    assert len(measurements) == 9


@pytest.mark.simulation
@pytest.mark.parametrize("engine_payload", ["solar_park"], indirect=True)
def test_simulation_measurements_contain_correct_asset_id_and_timestamps(
    engine_payload,
):
    measurements = simulate_asset_power_grid(
        engine_payload["config"],
        engine_payload["asset"],
    )
    asset = engine_payload["asset"]

    assert all(
        measurement.asset_id == asset.asset_id
        for measurement in measurements
    )

    expected_time_grid = generate_time_grid(
        engine_payload["config"].start_time,
        engine_payload["config"].end_time,
        engine_payload["config"].interval_minutes,
    )

    assert [
        measurement.measurement_time
        for measurement in measurements
    ] == expected_time_grid


# ============================================================
# Solar tests
# ============================================================


@pytest.mark.simulation
@pytest.mark.parametrize("engine_payload", ["solar_park"], indirect=True)
def test_online_solar_asset_returns_rated_power_at_peak(engine_payload):
    active_power_kw = simulate_power_of_asset(
        engine_payload["asset"],
        engine_payload["context"],
        engine_payload["profile_data"],
    )

    assert active_power_kw == pytest.approx(40_000.0)


@pytest.mark.simulation
@pytest.mark.parametrize("engine_payload", ["solar_park"], indirect=True)
def test_solar_asset_returns_zero_before_sunrise(engine_payload):
    context_before_sunrise = replace(
        engine_payload["context"],
        current_time=datetime(2026, 7, 16, 3, 30),
    )

    active_power_kw = simulate_power_of_asset(
        engine_payload["asset"],
        context_before_sunrise,
        engine_payload["profile_data"],
    )

    assert active_power_kw == 0


@pytest.mark.simulation
@pytest.mark.parametrize("engine_payload", ["solar_park"], indirect=True)
def test_solar_asset_returns_zero_after_sunset(engine_payload):
    context_after_sunset = replace(
        engine_payload["context"],
        current_time=datetime(2026, 7, 16, 20, 30),
    )

    active_power_kw = simulate_power_of_asset(
        engine_payload["asset"],
        context_after_sunset,
        engine_payload["profile_data"],
    )

    assert active_power_kw == 0


@pytest.mark.simulation
@pytest.mark.parametrize("engine_payload", ["solar_park"], indirect=True)
def test_solar_factor_scales_active_power(engine_payload):
    context_with_solar_factor = replace(
        engine_payload["context"],
        solar_factor=0.75,
    )

    active_power_kw = simulate_power_of_asset(
        engine_payload["asset"],
        context_with_solar_factor,
        engine_payload["profile_data"],
    )

    assert active_power_kw == pytest.approx(30_000.0)


@pytest.mark.simulation
@pytest.mark.parametrize("engine_payload", ["solar_park"], indirect=True)
def test_solar_power_above_rated_power_raises_value_error(engine_payload):
    context_with_high_solar_factor = replace(
        engine_payload["context"],
        solar_factor=1.5,
    )

    with pytest.raises(ValueError, match="exceeds rated power"):
        simulate_power_of_asset(
            engine_payload["asset"],
            context_with_high_solar_factor,
            engine_payload["profile_data"],
        )


@pytest.mark.simulation
@pytest.mark.parametrize("engine_payload", ["solar_park"], indirect=True)
def test_negative_solar_factor_raises_value_error(engine_payload):
    context_with_negative_solar_factor = replace(
        engine_payload["context"],
        solar_factor=-1.5,
    )

    with pytest.raises(ValueError, match="is negative"):
        simulate_power_of_asset(
            engine_payload["asset"],
            context_with_negative_solar_factor,
            engine_payload["profile_data"],
        )


# ============================================================
# Wind tests
# ============================================================


@pytest.mark.simulation
@pytest.mark.parametrize("engine_payload", ["wind_park"], indirect=True)
def test_wind_simulation_is_reproducible_with_same_seed(engine_payload):
    """Verify that identical seeds reproduce the complete wind simulation."""

    first_measurements = simulate_asset_power_grid(
        engine_payload["config"],
        engine_payload["asset"],
    )
    second_measurements = simulate_asset_power_grid(
        engine_payload["config"],
        engine_payload["asset"],
    )

    assert first_measurements == second_measurements


@pytest.mark.simulation
@pytest.mark.parametrize("engine_payload", ["wind_park"], indirect=True)
def test_wind_differs_with_different_seed(engine_payload):
    """Verify that a changed seed produces a different wind sequence."""

    config_with_new_seed = replace(
        engine_payload["config"],
        random_seed=2,
    )

    first_measurements = simulate_asset_power_grid(
        engine_payload["config"],
        engine_payload["asset"],
    )
    second_measurements = simulate_asset_power_grid(
        config_with_new_seed,
        engine_payload["asset"],
    )

    assert first_measurements != second_measurements


@pytest.mark.simulation
@pytest.mark.parametrize("engine_payload", ["wind_park"], indirect=True)
def test_wind_power_stays_within_expected_range(engine_payload):
    """Verify the modeled wind power range across several random seeds."""

    rated_power_kw = engine_payload["asset"].rated_power_kw
    minimum_power_kw = 0.70 * rated_power_kw

    for seed in range(41):
        config_with_new_seed = replace(
            engine_payload["config"],
            random_seed=seed,
        )
        measurements = simulate_asset_power_grid(
            config=config_with_new_seed,
            asset=engine_payload["asset"],
        )

        for measurement in measurements:
            assert (
                minimum_power_kw
                <= measurement.active_power_kw
                <= rated_power_kw
            )


@pytest.mark.simulation
@pytest.mark.parametrize("engine_payload", ["wind_park"], indirect=True)
def test_wind_factor_scales_active_power(engine_payload):
    """Isolate wind-factor scaling with fresh generators using one seed."""

    seed = engine_payload["config"].random_seed

    original_context = replace(
        engine_payload["context"],
        random_generator=Random(seed),
    )
    reduced_context = replace(
        engine_payload["context"],
        wind_factor=0.5,
        random_generator=Random(seed),
    )

    original_power_kw = simulate_power_of_asset(
        engine_payload["asset"],
        original_context,
        engine_payload["profile_data"],
    )
    reduced_power_kw = simulate_power_of_asset(
        engine_payload["asset"],
        reduced_context,
        engine_payload["profile_data"],
    )

    factor_difference = (
        original_context.wind_factor
        - reduced_context.wind_factor
    )
    expected_reduced_power_kw = (
        original_power_kw
        - factor_difference * engine_payload["asset"].rated_power_kw
    )

    assert reduced_power_kw == pytest.approx(expected_reduced_power_kw)


# ============================================================
# Hydro tests
# ============================================================


@pytest.mark.simulation
@pytest.mark.parametrize("engine_payload", ["hydro_power_plant"], indirect=True)
def test_hydro_factor_scales_active_power(engine_payload):
    hydro_factor = 0.5
    context_with_hydro_factor = replace(
        engine_payload["context"],
        hydro_factor=hydro_factor,
    )

    active_power_kw = simulate_power_of_asset(
        engine_payload["asset"],
        context_with_hydro_factor,
        engine_payload["profile_data"],
    )

    expected_power_kw = (
        engine_payload["asset"].rated_power_kw * hydro_factor
    )
    assert active_power_kw == pytest.approx(expected_power_kw)


# ============================================================
# Biomass tests
# ============================================================


@pytest.mark.simulation
@pytest.mark.parametrize("engine_payload", ["biomass_power_plant"], indirect=True)
def test_biomass_factor_scales_active_power(engine_payload):
    biomass_factor = 0.5
    context_with_biomass_factor = replace(
        engine_payload["context"],
        biomass_factor=biomass_factor,
    )

    active_power_kw = simulate_power_of_asset(
        engine_payload["asset"],
        context_with_biomass_factor,
        engine_payload["profile_data"],
    )

    expected_power_kw = (
        engine_payload["asset"].rated_power_kw * biomass_factor
    )
    assert active_power_kw == pytest.approx(expected_power_kw)
