from datetime import datetime

from src.measurements.models import PowerMeasurement


def create_power_measurement(
    measurement_time: datetime,
    active_power_kw: float,
    *,
    asset_id: int = 1,
    source: str = "simulation",
    quality_status: str = "valid",
) -> PowerMeasurement:
    """Create a power measurement for tests."""
    return PowerMeasurement(
        asset_id=asset_id,
        measurement_time=measurement_time,
        active_power_kw=active_power_kw,
        source=source,
        quality_status=quality_status,
    )