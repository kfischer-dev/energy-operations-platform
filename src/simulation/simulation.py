from datetime import time
from random import Random

from src.simulation.time_grid import generate_time_grid
from src.simulation.profiles import  time_to_minutes
from src.simulation.default_data import create_default_simulation_config, create_default_solar_asset, create_default_solar_context
from src.simulation.engine import simulate_power_of_asset


def simulate_solar_power_grid() -> list[float]:

    config = create_default_simulation_config()
    random_generator = Random(config.random_seed)
    asset = create_default_solar_asset()

    simulation_time_grid  = generate_time_grid(config.start_time, config.end_time, config.interval_minutes)

    # Preliminary Asset and Profile Parameter
    sunrise_time = time(6, 30, 0)
    sunset_time = time(18, 30, 0)
    peak_time = time(12, 30, 0)
    
    sun_profile= {
        "sunrise_minutes": time_to_minutes(sunrise_time),
        "sunset_minutes": time_to_minutes(sunset_time),
        "peak_minutes": time_to_minutes(peak_time)
    }

    active_power_grid: list[float] = []

    for timestamp in simulation_time_grid:
        solar_context = create_default_solar_context(
            config=config,
            current_time=timestamp,
            random_generator=random_generator,
        )
        active_power_kw = simulate_power_of_asset(asset, solar_context, sun_profile)
        active_power_grid.append(active_power_kw)
    print(active_power_grid,2)
    return active_power_grid

if __name__ == "__main__":
    simulate_solar_power_grid()