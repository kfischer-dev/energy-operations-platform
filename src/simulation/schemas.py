from datetime import datetime, timedelta
from typing import Literal, Self

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator

from src.simulation.models import SimulationConfig


class SimulationRunCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    simulation_mode: Literal["historical"]
    start_time: AwareDatetime
    end_time: AwareDatetime
    interval_minutes: Literal[15, 30, 60]
    random_seed: int = Field(..., ge=0, le=2_147_483_647, strict=True)

    @model_validator(mode="after")
    def validate_period(self) -> Self:
        config = self.to_simulation_config()
        if config.duration > timedelta(hours=24):
            raise ValueError("Simulation period must not exceed 24 hours.")
        if config.duration % timedelta(minutes=config.interval_minutes):
            raise ValueError("Simulation period must be divisible by interval_minutes.")
        return self

    def to_simulation_config(self) -> SimulationConfig:
        return SimulationConfig(**self.model_dump())


class SimulationRunResponse(BaseModel):
    simulation_run_id: int = Field(..., ge=1)
    simulation_mode: Literal["historical", "live", "forecast", "scenario"]
    start_time: datetime
    end_time: datetime
    interval_minutes: int = Field(..., ge=1)
    random_seed: int | None = None
    status: Literal["created", "running", "completed", "failed"]
    generated_measurement_count: int = Field(..., ge=0)
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
