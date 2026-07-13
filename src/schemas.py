from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class AssetResponse(BaseModel):
    asset_id: int
    asset_name: str
    asset_type: str
    asset_location: str

class MeasurementResponse(BaseModel):
    asset_name: str
    measurement_time: datetime
    load_value: float
    unit: str

class MeasurementCreate(BaseModel):
    asset_id: int = Field(..., ge=1)
    measurement_time: datetime
    load_value: float = Field(..., ge=0)
    unit: Literal["kW", "MW"]
    source: str = Field(..., min_length=1)
    quality_status: Literal["valid", "invalid", "estimated"]

class MeasurementDetailResponse(BaseModel):
    measurement_id: int
    asset_id: int
    measurement_time: datetime
    load_value: float
    unit: str
    source: str
    quality_status: str

class MeasurementQualityUpdate(BaseModel):
    quality_status: Literal["valid", "invalid", "estimated"]

class MeasurementKPIsResponse(BaseModel):
    measurement_count: int = Field(..., ge=0)
    average_load: float | None
    min_load: float | None
    max_load: float | None
    latest_measurement_time: datetime | None

class AssetKPIsResponse(BaseModel):
    asset_id: int = Field(..., ge=1)
    asset_name: str
    measurement_count: int = Field(..., ge=0)
    average_load: float | None
    min_load: float | None
    max_load: float | None
    latest_measurement_time: datetime | None