from datetime import datetime
from random import Random

from src.simulation.models import (
    SimulationAsset,
    SimulationConfig,
    SimulationContext,
)

# ============================================================
# General
# ============================================================


def create_default_simulation_config() -> SimulationConfig:
    """Create the default configuration used for local simulations and tests."""

    config = SimulationConfig(
        start_time=datetime(2026, 7, 16, 12, 0, 0),
        end_time=datetime(2026, 7, 16, 14, 0, 0),
        interval_minutes=15,
        random_seed=1,
        simulation_mode="historical",
    )
    return config


# ============================================================
# Solar Park
# ============================================================


def create_default_solar_asset() -> SimulationAsset:
    """Create the default solar asset used by the simulation."""

    solar_asset = SimulationAsset(
        asset_id=2,
        asset_code="N-SOLAR-001",
        asset_role="producer",
        asset_type="solar_park",
        region_id=1,
        region_code="DE-NORTH",
        rated_power_kw=40_000,
        operating_status="online",
        is_renewable=True,
        is_weather_dependent=True,
        is_dispatchable=False,
        can_store_energy=False,
    )

    return solar_asset


def create_default_solar_context(
    config: SimulationConfig,
    current_time: datetime,
    random_generator: Random,
) -> SimulationContext:
    """Create a solar simulation context for one timestamp."""

    solar_context = SimulationContext(
        config=config,
        current_time=current_time,
        random_generator=random_generator,
        solar_factor=1.0,
        wind_factor=0.0,
        load_factor=0.0,
        hydro_factor=0.0,
        biomass_factor=0.0,
    )

    return solar_context


# ============================================================
# Wind Park
# ============================================================


def create_default_wind_park_asset() -> SimulationAsset:
    """Create the default wind asset used by the simulation."""

    return SimulationAsset(
        asset_id=1,
        asset_code="N-WIND-001",
        asset_role="producer",
        asset_type="wind_park",
        region_id=1,
        region_code="DE-NORTH",
        rated_power_kw=120_000,
        operating_status="online",
        is_renewable=True,
        is_weather_dependent=True,
        is_dispatchable=False,
        can_store_energy=False,
    )


def create_default_wind_park_context(
    config: SimulationConfig,
    current_time: datetime,
    random_generator: Random,
) -> SimulationContext:
    """Create a wind simulation context for one timestamp."""

    return SimulationContext(
        config=config,
        current_time=current_time,
        random_generator=random_generator,
        solar_factor=0.0,
        wind_factor=0.85,
        load_factor=0.0,
        hydro_factor=0.0,
        biomass_factor=0.0,
    )


# ============================================================
# Hydro Power Plant
# ============================================================


def create_default_hydro_plant_asset() -> SimulationAsset:
    """Create the default hydro asset used by the simulation."""

    return SimulationAsset(
        asset_id=5,
        asset_code="S-HYDRO-001",
        asset_role="producer",
        asset_type="hydro_power_plant",
        region_id=2,
        region_code="DE-SOUTH",
        rated_power_kw=80_000,
        operating_status="online",
        is_renewable=True,
        is_weather_dependent=True,
        is_dispatchable=True,
        can_store_energy=False,
    )


def create_default_hydro_plant_context(
    config: SimulationConfig,
    current_time: datetime,
    random_generator: Random,
) -> SimulationContext:
    """Create a hydro simulation context for one timestamp."""

    return SimulationContext(
        config=config,
        current_time=current_time,
        random_generator=random_generator,
        solar_factor=0.0,
        wind_factor=0.0,
        load_factor=0.0,
        hydro_factor=0.9,
        biomass_factor=0.0,
    )


# ============================================================
# Biomass power plant defaults
# ============================================================


def create_default_biomass_asset() -> SimulationAsset:
    """Create the default biomass asset used by the simulation."""

    return SimulationAsset(
        asset_id=10,
        asset_code="E-BIO-001",
        asset_role="producer",
        asset_type="biomass_power_plant",
        region_id=3,
        region_code="DE-EAST",
        rated_power_kw=50_000,
        operating_status="online",
        is_renewable=True,
        is_weather_dependent=False,
        is_dispatchable=True,
        can_store_energy=False,
    )


def create_default_biomass_context(
    config: SimulationConfig,
    current_time: datetime,
    random_generator: Random,
) -> SimulationContext:
    """Create a biomass simulation context for one timestamp."""

    return SimulationContext(
        config=config,
        current_time=current_time,
        random_generator=random_generator,
        solar_factor=0.0,
        wind_factor=0.0,
        load_factor=0.0,
        hydro_factor=0.0,
        biomass_factor=0.85,
    )
