from dataclasses import FrozenInstanceError, replace
from datetime import datetime
from random import Random

import pytest

from src.simulation.default_data import create_default_simulation_config
from src.simulation.engine import simulate_assets_power_grid
from src.simulation.registry import SIMULATION_PROFILE_REGISTRY
from src.simulation.scenarios import SCENARIOS, ScenarioFactors, get_scenario
from src.simulation.simulation import (
    build_profile_data,
    create_simulation_context,
    simulate_asset_power_grid,
    simulate_power_of_asset,
)

pytestmark = [pytest.mark.simulation, pytest.mark.scenarios]


def test_scenarios_are_fixed_and_have_expected_effects():
    assert set(SCENARIOS) == {
        "baseline",
        "cloudy_day",
        "windy_day",
        "high_demand",
        "energy_stress",
    }
    assert get_scenario("cloudy_day").solar < 1
    assert get_scenario("windy_day").wind > 1
    assert get_scenario("high_demand").load > 1
    stress = get_scenario("energy_stress")
    assert stress.solar < 1 and stress.wind < 1 and stress.load > 1
    with pytest.raises(ValueError, match="Unknown simulation scenario"):
        get_scenario("unknown")
    with pytest.raises(TypeError):
        SCENARIOS["new"] = ScenarioFactors()
    with pytest.raises(FrozenInstanceError):
        stress.solar = 1


@pytest.mark.parametrize(
    ("asset_type", "profile"),
    [
        ("solar_park", "solar"),
        ("wind_park", "wind"),
        ("hydro_power_plant", "hydro"),
        ("biomass_power_plant", "biomass"),
        ("city_load", "load"),
        ("industrial_load", "load"),
    ],
)
def test_baseline_preserves_existing_profile_results(asset_type, profile):
    config = create_default_simulation_config()
    asset = SIMULATION_PROFILE_REGISTRY[asset_type].default_asset_factory()
    random_generator = Random(config.random_seed)
    for hour in (0, 6, 12, 18, 23):
        context = create_simulation_context(
            config, asset, datetime(2026, 7, 16, hour), random_generator
        )
        power = simulate_power_of_asset(asset, context, build_profile_data(asset))
        assert (
            get_scenario("baseline").scale_power(profile, power, asset.rated_power_kw)
            == power
        )


@pytest.mark.parametrize("invalid", [-0.1, 2.1, float("nan"), float("inf"), True])
def test_invalid_factors_are_rejected(invalid):
    with pytest.raises(ValueError, match="solar factor"):
        ScenarioFactors(solar=invalid)


def test_scaled_power_respects_rated_power_and_rejects_invalid_input():
    windy = get_scenario("windy_day")
    demand = get_scenario("high_demand")
    assert windy.scale_power("wind", 50, 100) == 60
    assert windy.scale_power("wind", 95, 100) == 100
    assert demand.scale_power("load", 90, 100) == 100
    assert get_scenario("cloudy_day").scale_power("solar", 50, 100) == 20
    for power, rated in [(-1, 100), (101, 100), (float("nan"), 100), (0, -1)]:
        with pytest.raises(ValueError):
            windy.scale_power("wind", power, rated)
    with pytest.raises(ValueError, match="Unknown profile kind"):
        windy.scale_power("other", 50, 100)


def test_configuration_defaults_to_baseline_and_rejects_unknown_scenario():
    config = create_default_simulation_config()
    assert config.scenario == "baseline"
    with pytest.raises(ValueError, match="Unknown simulation scenario"):
        replace(config, scenario="unknown")


@pytest.mark.parametrize("asset_type", list(SIMULATION_PROFILE_REGISTRY))
def test_default_baseline_matches_original_profile(asset_type):
    config = create_default_simulation_config()
    definition = SIMULATION_PROFILE_REGISTRY[asset_type]
    asset = definition.default_asset_factory()
    rng_expected = Random(config.random_seed)
    rng_actual = Random(config.random_seed)
    for hour in (0, 6, 12, 18, 23):
        timestamp = datetime(2026, 7, 16, hour)
        expected_context = create_simulation_context(
            config, asset, timestamp, rng_expected
        )
        actual_context = create_simulation_context(config, asset, timestamp, rng_actual)
        profile_data = build_profile_data(asset)
        expected = definition.power_profile(asset, expected_context, profile_data)
        assert simulate_power_of_asset(asset, actual_context, profile_data) == expected


@pytest.mark.parametrize(
    ("scenario", "asset_type", "factor"),
    [
        ("cloudy_day", "solar_park", 0.4),
        ("windy_day", "wind_park", 1.2),
        ("high_demand", "city_load", 1.15),
        ("high_demand", "industrial_load", 1.15),
        ("energy_stress", "solar_park", 0.4),
        ("energy_stress", "wind_park", 0.5),
        ("energy_stress", "city_load", 1.15),
    ],
)
def test_scenario_scales_profile_after_seeded_generation(scenario, asset_type, factor):
    config = create_default_simulation_config()
    asset = SIMULATION_PROFILE_REGISTRY[asset_type].default_asset_factory()
    baseline = simulate_asset_power_grid(config, asset)
    changed = simulate_asset_power_grid(replace(config, scenario=scenario), asset)

    assert [point.measurement_time for point in changed] == [
        point.measurement_time for point in baseline
    ]
    assert any(
        a.active_power_kw != b.active_power_kw for a, b in zip(baseline, changed)
    )
    for original, actual in zip(baseline, changed):
        assert actual.active_power_kw == pytest.approx(
            min(original.active_power_kw * factor, asset.rated_power_kw)
        )
        assert 0 <= actual.active_power_kw <= asset.rated_power_kw


@pytest.mark.parametrize("scenario", list(SCENARIOS))
def test_scenarios_are_reproducible_and_respect_rated_power(scenario):
    config = replace(create_default_simulation_config(), scenario=scenario)
    assets = [
        definition.default_asset_factory()
        for definition in SIMULATION_PROFILE_REGISTRY.values()
    ]
    first = simulate_assets_power_grid(config, assets)
    assert first == simulate_assets_power_grid(config, assets)
    limits = {asset.asset_id: asset.rated_power_kw for asset in assets}
    assert all(0 <= point.active_power_kw <= limits[point.asset_id] for point in first)


def test_windy_scenario_keeps_seeded_variation_and_caps_peaks():
    config = replace(create_default_simulation_config(), scenario="windy_day")
    asset = SIMULATION_PROFILE_REGISTRY["wind_park"].default_asset_factory()
    first = simulate_asset_power_grid(config, asset)
    second = simulate_asset_power_grid(replace(config, random_seed=2), asset)
    assert first != second
    assert any(point.active_power_kw == asset.rated_power_kw for point in first)
    assert any(point.active_power_kw < asset.rated_power_kw for point in first)
