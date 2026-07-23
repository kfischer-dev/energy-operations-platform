from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from random import Random

from src.simulation.default_data import (
    create_default_biomass_asset,
    create_default_biomass_context,
    create_default_hydro_plant_asset,
    create_default_hydro_plant_context,
    create_default_solar_asset,
    create_default_solar_context,
    create_default_wind_park_asset,
    create_default_wind_park_context,
)
from src.simulation.models import (
    SimulationAsset,
    SimulationConfig,
    SimulationContext,
)
from src.simulation.profiles import (
    calculate_biomass_power_kw,
    calculate_hydro_power_kw,
    calculate_solar_power_kw,
    calculate_wind_power_kw,
)

# ============================================================
# Simulation Profile Class
# ============================================================

PowerProfileFunction = Callable[
    [
        SimulationAsset,
        SimulationContext,
        dict[str, dict[str, int]],
    ],
    float,
]
DefaultAssetFactory = Callable[[], SimulationAsset]
ContextFactory = Callable[
    [
        SimulationConfig,
        datetime,
        Random,
    ],
    SimulationContext,
]


@dataclass(frozen=True)
class SimulationProfileDefinition:
    """Bundle all simulation behavior required by one asset type."""

    power_profile: PowerProfileFunction
    default_asset_factory: DefaultAssetFactory
    context_factory: ContextFactory


# ============================================================
# Simulation Profile Registry
# ============================================================

SIMULATION_PROFILE_REGISTRY: dict[str, SimulationProfileDefinition] = {
    "solar_park": SimulationProfileDefinition(
        power_profile=calculate_solar_power_kw,
        default_asset_factory=create_default_solar_asset,
        context_factory=create_default_solar_context,
    ),
    "wind_park": SimulationProfileDefinition(
        power_profile=calculate_wind_power_kw,
        default_asset_factory=create_default_wind_park_asset,
        context_factory=create_default_wind_park_context,
    ),
    "hydro_power_plant": SimulationProfileDefinition(
        power_profile=calculate_hydro_power_kw,
        default_asset_factory=create_default_hydro_plant_asset,
        context_factory=create_default_hydro_plant_context,
    ),
    "biomass_power_plant": SimulationProfileDefinition(
        power_profile=calculate_biomass_power_kw,
        default_asset_factory=create_default_biomass_asset,
        context_factory=create_default_biomass_context,
    ),
}
