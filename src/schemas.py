from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


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


class MeasurementKPIsResponse(BaseModel):
    measurement_count: int = Field(..., ge=0)
    average_power_kw: float | None
    min_power_kw: float | None
    max_power_kw: float | None
    total_energy_kwh: float | None
    latest_measurement_time: datetime | None


class AssetKPIsResponse(BaseModel):
    asset_id: int = Field(..., ge=1)
    asset_name: str
    period_start: datetime
    period_end: datetime
    measurement_count: int = Field(..., ge=0)
    min_measured_power_kw: float | None
    max_measured_power_kw: float | None
    average_power_kw: float | None
    total_energy_kwh: float | None
    coverage_ratio: float | None
