from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_serializer


class AssetResponse(BaseModel):
    asset_id: int = Field(..., ge=1)
    asset_name: str
    asset_code: str
    asset_location: str
    asset_role: str
    asset_type: str
    region_id: int = Field(..., ge=1)
    region_code: str
    region_name: str
    rated_power_kw: float = Field(..., ge=0)
    latitude: float
    longitude: float
    operating_status: Literal["online", "offline", "maintenance", "fault"]


class AssetSummaryResponse(BaseModel):
    asset_id: int = Field(..., ge=1)
    asset_name: str
    asset_code: str
    asset_location: str
    asset_role: str
    asset_type: str
    region_code: str
    rated_power_kw: float = Field(..., ge=0)
    operating_status: Literal["online", "offline", "maintenance", "fault"]


class MeasurementResponse(BaseModel):
    measurement_id: int = Field(..., ge=1)
    asset_id: int = Field(..., ge=1)
    asset_code: str
    asset_name: str
    asset_type: str
    asset_role: str
    region_code: str
    measurement_time: datetime
    active_power_kw: float
    source: str = Field(..., min_length=1)
    quality_status: Literal["valid", "invalid", "estimated"]


class MeasurementSummaryResponse(BaseModel):
    measurement_id: int = Field(..., ge=1)
    asset_code: str
    asset_name: str
    asset_id: int = Field(..., ge=1)
    measurement_time: datetime
    active_power_kw: float
    quality_status: Literal["valid", "invalid", "estimated"]


class MeasurementCreate(BaseModel):
    asset_id: int = Field(..., ge=1)
    measurement_time: datetime
    active_power_kw: float
    source: str = Field(..., min_length=1)
    quality_status: Literal["valid", "invalid", "estimated"]


class MeasurementQualityUpdate(BaseModel):
    quality_status: Literal["valid", "invalid", "estimated"]


class KPIResponseBase(BaseModel):
    period_start: datetime
    period_end: datetime
    measurement_count: int = Field(..., ge=0)
    min_measured_power_kw: float | None
    max_measured_power_kw: float | None
    avg_active_power_kw: float | None = Field(
        default=None,
        description=(
            "Time-weighted average active power over the covered portion "
            "of the requested period. If coverage_ratio is below 1.0, "
            "the value does not represent the entire requested period."
        ),
    )
    total_energy_kwh: float | None = Field(
        default=None,
        description=(
            "Total energy calculated over the covered portion of the requested period."
        ),
    )
    coverage_ratio: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description=(
            "Fraction of the requested period covered by valid measurement data. "
            "A value of 1.0 represents full coverage."
        ),
    )


class MeasurementKPIsResponse(KPIResponseBase):
    pass


class AssetKPIsResponse(KPIResponseBase):
    asset_id: int = Field(..., ge=1)
    asset_name: str


class BalanceSummaryResponse(BaseModel):
    start_time: datetime
    end_time: datetime

    total_production_energy_kwh: float
    total_consumption_energy_kwh: float
    total_net_energy_kwh: float

    quality_status: Literal["valid", "incomplete", "invalid", "estimated"]

    @field_serializer(
        "total_production_energy_kwh",
        "total_consumption_energy_kwh",
        "total_net_energy_kwh",
    )
    def serialize_energy(self, value: float) -> float:
        return round(value, 2)


class BalanceIntervalResponse(BaseModel):
    interval_start: datetime
    interval_end: datetime
    avg_production_power_kw: float
    avg_consumption_power_kw: float
    avg_net_power_kw: float

    production_energy_kwh: float
    consumption_energy_kwh: float
    net_energy_kwh: float

    quality_status: Literal["valid", "incomplete", "invalid", "estimated"]

    @field_serializer(
        "avg_production_power_kw",
        "avg_consumption_power_kw",
        "avg_net_power_kw",
        "production_energy_kwh",
        "consumption_energy_kwh",
        "net_energy_kwh",
    )
    def serialize_values(self, value: float) -> float:
        return round(value, 2)


class EnergyMixContributionResponse(BaseModel):
    asset_type: str
    energy_kwh: float
    share_percent: float
    asset_count: int

    @field_serializer("energy_kwh", "share_percent")
    def serialize_share_percent(self, value: float) -> float:
        return round(value, 2)


class EnergyMixResponse(BaseModel):
    start_time: datetime
    end_time: datetime

    asset_role: Literal["producer", "consumer"]
    total_energy_kwh: float

    contributions: list[EnergyMixContributionResponse]
    
    quality_status: Literal["valid", "incomplete", "estimated", "invalid"]

    @field_serializer("total_energy_kwh")
    def serialize_total_energy(self, value: float) -> float:
        return round(value, 2)
