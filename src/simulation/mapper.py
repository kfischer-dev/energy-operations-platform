from src.simulation.models import SimulationAsset

# ============================================================
# Domain Mapper
# ============================================================


def map_asset_to_simulation_asset(asset: dict) -> SimulationAsset:
    """Convert a database asset dictionary into a simulation asset."""

    return SimulationAsset(
        asset_id=asset["asset_id"],
        asset_code=asset["asset_code"],
        asset_role=asset["asset_role"],
        asset_type=asset["asset_type"],
        region_id=asset["region_id"],
        region_code=asset["region_code"],
        rated_power_kw=float(asset["rated_power_kw"]),
        operating_status=asset["operating_status"],
        is_renewable=asset["is_renewable"],
        is_weather_dependent=asset["is_weather_dependent"],
        is_dispatchable=asset["is_dispatchable"],
        can_store_energy=asset["can_store_energy"],
    )



# ============================================================
# Repository Mapper
# ============================================================


def map_simulation_asset_row(row) -> dict:
    (
        asset_id,
        asset_code,
        asset_role,
        asset_type,
        region_id,
        region_code,
        rated_power_kw,
        operating_status,
        is_renewable,
        is_weather_dependent,
        is_dispatchable,
        can_store_energy,
    ) = row

    return {
        "asset_id": asset_id,
        "asset_code": asset_code,
        "asset_role": asset_role,
        "asset_type": asset_type,
        "region_id": region_id,
        "region_code": region_code,
        "rated_power_kw": rated_power_kw,
        "operating_status": operating_status,
        "is_renewable": is_renewable,
        "is_weather_dependent": is_weather_dependent,
        "is_dispatchable": is_dispatchable,
        "can_store_energy": can_store_energy,
    }


def map_simulation_run_row(row) -> dict:
    (
        simulation_run_id,
        simulation_mode,
        start_time,
        end_time,
        interval_minutes,
        random_seed,
        status,
        created_at,
        started_at,
        completed_at,
        generated_measurement_count,
    ) = row

    return {
        "simulation_run_id": simulation_run_id,
        "simulation_mode": simulation_mode,
        "start_time": start_time,
        "end_time": end_time,
        "interval_minutes": interval_minutes,
        "random_seed": random_seed,
        "status": status,
        "created_at": created_at,
        "started_at": started_at,
        "completed_at": completed_at,
        "generated_measurement_count": generated_measurement_count,
    }
