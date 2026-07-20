from src.simulation.models import SimulationAsset, SimulationContext
from src.simulation.registry import POWER_PROFILE_REGISTRY


def simulate_power_of_asset(
    asset: SimulationAsset,
    context: SimulationContext,
    profile_data: dict[str, dict[str, int]],
) -> float:
    """Calculate active power for one asset at one simulation timestamp."""

    if asset.operating_status != "online":
        return 0.0

    profile_function = POWER_PROFILE_REGISTRY.get(asset.asset_type)

    if profile_function is None:
        raise NotImplementedError(
            f"Asset type '{asset.asset_type}' is not supported yet."
        )

    final_active_power_kw = profile_function(
        asset=asset,
        context=context,
        profile_data=profile_data,
    )

    if final_active_power_kw > asset.rated_power_kw:
        raise ValueError(
            f"Active power of {asset.asset_code} exceeds rated power!"
        )

    if final_active_power_kw < 0:
        raise ValueError(
            f"Active power of {asset.asset_code} is negative!"
        )

    return final_active_power_kw
