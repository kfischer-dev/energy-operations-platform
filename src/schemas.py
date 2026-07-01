from datetime import datetime

from pydantic import BaseModel


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