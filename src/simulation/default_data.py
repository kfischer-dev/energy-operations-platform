from src.simulation.models import SimulationAsset, SimulationContext, SimulationConfig
from random import Random
from datetime import datetime

def create_default_solar_asset() -> SimulationAsset:
    solar_asset = SimulationAsset(
        asset_id=1,
        asset_code="N-SOLAR-001",
        asset_role="producer",
        asset_type="solar_park",
        region_id=1,
        region_code="DE-NORTH",
        rated_power_kw=50_000,
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

    solar_context = SimulationContext(
        config=config,
        current_time=current_time,
        random_generator=random_generator,
        solar_factor=1.0,
        wind_factor=0.0,
        load_factor=1.0,
    )

    return solar_context

def create_default_simulation_config() -> SimulationConfig:
    config = SimulationConfig(
        start_time=datetime(2026, 7, 16, 12, 0, 0),
        end_time=datetime(2026, 7, 16, 14, 0, 0),
        interval_minutes=15,
        random_seed=1,
        simulation_mode='live'
    )
    return config