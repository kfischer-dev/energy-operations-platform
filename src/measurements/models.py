from dataclasses import dataclass
from datetime import datetime
from typing import Literal


MeasurementSource = Literal[
    "simulation",
    "database",
    "scada",
    "smart_meter",
    "csv_import",
    "external_api",
]

MeasurementQualityStatus = Literal[
    "valid",
    "invalid",
    "estimated",
    "interpolated",
]

SupportPointType = Literal[
    "measured",
    "interpolated",
    "estimated",
]

IntervalQualityStatus = Literal[
    "valid",
    "incomplete",
    "estimated",
    "invalid",
]


@dataclass(frozen=True)
class PowerMeasurement:
    """Represents one instantaneous active-power measurement."""

    asset_id: int
    measurement_time: datetime
    active_power_kw: float
    source: MeasurementSource
    quality_status: MeasurementQualityStatus = "valid"


@dataclass(frozen=True)
class PowerSupportPoint:
    """Represents a temporary point used during interval aggregation."""

    timestamp: datetime
    active_power_kw: float
    point_type: SupportPointType
    is_interpolated: bool = False


@dataclass(frozen=True)
class PowerIntervalDraft:
    """Represents an aggregated power interval before persistence."""

    asset_id: int
    interval_start: datetime
    interval_end: datetime
    avg_active_power_kw: float | None
    energy_kwh: float | None
    quality_status: IntervalQualityStatus
    aggregation_method: str
    source_measurement_count: int
    valid_measurement_count: int
    coverage_ratio: float


@dataclass(frozen=True)
class PowerSegment:
    """Represents one segment between two adjacent support points."""

    start_point: PowerSupportPoint
    end_point: PowerSupportPoint
