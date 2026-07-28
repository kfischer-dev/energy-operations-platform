from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SimulationRuns(BaseModel):
    simulation_run_id: int = Field(..., ge=1)
    simulation_mode: Literal["historical", "live", "forecast", "scenario"]
    start_time: datetime
    end_time: datetime
    interval_minutes: int = Field(..., ge=1)
    random_seed: int | None = None
    status: Literal["pending", "running", "completed", "failed"]
    generated_measurement_count: int = Field(..., ge=0)
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
