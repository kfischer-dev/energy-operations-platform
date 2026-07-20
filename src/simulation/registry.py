from collections.abc import Callable
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
# Power Profile Registry
# ============================================================

PowerProfileFunction = Callable[
    [
        SimulationAsset,
        SimulationContext,
        dict[str, dict[str, int]],
    ],
    float,
]

POWER_PROFILE_REGISTRY: dict[str, PowerProfileFunction] = {
    "solar_park": calculate_solar_power_kw,
    "wind_park": calculate_wind_power_kw,
    "hydro_power_plant": calculate_hydro_power_kw,
    "biomass_power_plant": calculate_biomass_power_kw,
}

# ============================================================
# Default Asset Registry
# ============================================================

DefaultAssetFunction = Callable[[], SimulationAsset]

DEFAULT_ASSET_REGISTRY: dict[str, DefaultAssetFunction] = {
    "solar_park": create_default_solar_asset,
    "wind_park": create_default_wind_park_asset,
    "hydro_power_plant": create_default_hydro_plant_asset,
    "biomass_power_plant": create_default_biomass_asset,
}

# ============================================================
# Default Context Registry
# ============================================================

DefaultContextFunction = Callable[
    [
        SimulationConfig,
        datetime,
        Random,
    ],
    SimulationContext,
]

DEFAULT_CONTEXT_REGISTRY: dict[str, DefaultContextFunction] = {
    "solar_park": create_default_solar_context,
    "wind_park": create_default_wind_park_context,
    "hydro_power_plant": create_default_hydro_plant_context,
    "biomass_power_plant": create_default_biomass_context,
}
