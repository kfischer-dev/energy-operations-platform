from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class StationResponse(BaseModel):
    station_id: int
    station_name: str
    station_type: str
    station_location: str

class MeasurementResponse(BaseModel):
    station_name: str
    measurement_time: datetime
    load_value: float
    unit: str

class MeasurementCreate(BaseModel):
    station_id: int = Field(..., ge=1)
    measurement_time: datetime
    load_value: float = Field(..., ge=0)
    unit: Literal["kW", "MW"]
    source: str = Field(..., min_length=1)
    quality_status: Literal["valid", "invalid", "estimated"]

class MeasurementDetailResponse(BaseModel):
    measurement_id: int
    station_id: int
    measurement_time: datetime
    load_value: float
    unit: str
    source: str
    quality_status: str