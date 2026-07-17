from datetime import time
from random import Random
from datetime import datetime

from src.simulation.time_grid import generate_time_grid
from src.simulation.profiles import  time_to_minutes
from src.simulation.default_data import create_default_simulation_config, create_default_solar_asset, create_default_solar_context, create_default_wind_park_asset, create_default_wind_park_context, create_default_hydro_plant_asset, create_default_hydro_plant_context, create_default_biomass_asset, create_default_biomass_context
from src.simulation.engine import simulate_power_of_asset
from src.simulation.models import SimulationPowerMeasurementDraft, SimulationConfig, SimulationAsset, SimulationContext


def create_default_asset(asset_type: str) -> SimulationAsset:

    if asset_type == "solar_park":
        asset = create_default_solar_asset()

    elif asset_type == "wind_park":
        asset = create_default_wind_park_asset()

    elif asset_type == "hydro_power_plant":
        asset = create_default_hydro_plant_asset()

    elif asset_type == "biomass_power_plant":
        asset = create_default_biomass_asset()
    
    else:
        raise ValueError(f"Asset type '{asset_type}' not available for simulation.")

    return asset

def build_profile_data(asset: SimulationAsset) -> dict[str, dict[str, int]]:

    if asset.asset_type == "solar_park":
        # Preliminary Asset and Profile Parameter
        sunrise_time = time(6, 30, 0)
        sunset_time = time(18, 30, 0)
        peak_time = time(12, 30, 0)
        
        profile_data = {"solar_park": {
            "sunrise_minutes": time_to_minutes(sunrise_time),
            "sunset_minutes": time_to_minutes(sunset_time),
            "peak_minutes": time_to_minutes(peak_time)
        }}

    elif asset.asset_type == "wind_park":
        profile_data = {
        "wind_park": {
        }}

    elif asset.asset_type == "hydro_power_plant":
        profile_data = {
        "hydro_power_plant": {
        }}

    elif asset.asset_type == "biomass_power_plant":
        profile_data = {
        "biomass_power_plant": {
        }}
    
    else:
        raise ValueError(f"Asset type '{asset.asset_type}' not available for simulation.")

    return profile_data

def create_simulation_context(config: SimulationConfig, asset: SimulationAsset, timestamp: datetime, random_generator: Random):

    if asset.asset_type == "solar_park":
        return create_default_solar_context(
        config=config,
        current_time=timestamp,
        random_generator=random_generator,
        )
        
    elif asset.asset_type == "wind_park":
        return create_default_wind_park_context(
        config=config,
        current_time=timestamp,
        random_generator=random_generator,
        )

    elif asset.asset_type == "hydro_power_plant":
        return create_default_hydro_plant_context(
        config=config,
        current_time=timestamp,
        random_generator=random_generator,
        )

    elif asset.asset_type == "biomass_power_plant":
        return create_default_biomass_context(
        config=config,
        current_time=timestamp,
        random_generator=random_generator,
        )
    
    else:
        raise ValueError(f"Asset type '{asset.asset_type}' not available for simulation.")
    
def simulate_asset_power_grid(config: SimulationConfig, asset: SimulationAsset) -> list[SimulationPowerMeasurementDraft]:
    random_generator = Random(config.random_seed)
    simulation_time_grid  = generate_time_grid(config.start_time, config.end_time, config.interval_minutes)

    profile_data = build_profile_data(asset)

    power_measurement_list: list[SimulationPowerMeasurementDraft] = []

    for timestamp in simulation_time_grid:
        context = create_simulation_context(config, asset, timestamp, random_generator)
        active_power_kw = simulate_power_of_asset(asset, context, profile_data)

        power_measurement = SimulationPowerMeasurementDraft(
            asset_id=asset.asset_id,
            measurement_time=context.current_time,
            active_power_kw=active_power_kw,
        )
        power_measurement_list.append(power_measurement)
    
    return power_measurement_list

def simulation(asset_type: str):
    config = create_default_simulation_config()
    asset = create_default_asset(asset_type)

    simulated_power_measurement_list = simulate_asset_power_grid(config, asset)

    print(simulated_power_measurement_list)


if __name__ == "__main__":
    simulation("solar_park")
    simulation("wind_park")
    simulation("hydro_power_plant")
    simulation("biomass_power_plant")