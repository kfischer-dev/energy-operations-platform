from src.simulation.models import SimulationAsset, SimulationContext
from src.simulation.profiles import time_to_minutes, calculate_solar_power_kw

def simulate_power_of_asset(asset: SimulationAsset, context: SimulationContext, sun_profile: dict[str, int]) -> float:

    if asset.operating_status != "online":
        return 0.0
    
    if asset.asset_type == "solar_park":

        active_power_kw = calculate_solar_power_kw(
            rated_power_kw=asset.rated_power_kw,
            time_minutes=time_to_minutes(context.current_time.time()),
            sunrise_minutes=sun_profile["sunrise_minutes"],
            peak_minutes=sun_profile["peak_minutes"],
            sunset_minutes=sun_profile["sunset_minutes"],
        )

        final_active_power_kw = active_power_kw * context.solar_factor
        
        return final_active_power_kw
    
    else:
        raise NotImplementedError(f"Asset type '{asset.asset_type}' is not supported yet.")
    
