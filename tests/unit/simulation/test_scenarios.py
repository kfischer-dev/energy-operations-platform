from dataclasses import FrozenInstanceError
from datetime import datetime
from random import Random

import pytest

from src.simulation.default_data import create_default_simulation_config
from src.simulation.registry import SIMULATION_PROFILE_REGISTRY
from src.simulation.scenarios import SCENARIOS, ScenarioFactors, get_scenario
from src.simulation.simulation import (
    build_profile_data,
    create_simulation_context,
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
