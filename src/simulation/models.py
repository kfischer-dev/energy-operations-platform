from dataclasses import dataclass, field
from datetime import datetime, timedelta
from random import Random
from typing import Literal

@dataclass(frozen=True)
class SimulationConfig:
    """Stores validated configuration settings for measurement simulations."""

    start_time: datetime
    end_time: datetime
    # Supported intervals: 5, 15, 30 and 60 minutes.
    interval_minutes: int
    # Seed for reproducible random number generation.
    # The same seed always produces the same simulation results.
    random_seed: int
    # Defines how simulated measurements are generated:
    # historical = past data, live = continuous current data,
    # forecast = future data, scenario = predefined operating condition.
    simulation_mode: Literal["historical", "live", "forecast", "scenario"]

    
    # Non-aligned end times are allowed.
    # The simulation generates only complete intervals up to the last valid timestamp.
    def __post_init__(self):
        if self.start_time >= self.end_time:
            raise ValueError("start_time must be before end_time")
        if self.interval_minutes not in [5, 15, 30, 60]:
            raise ValueError("Unsupported interval_minutes. Supported values are 5, 15, 30, and 60.")
        if self.simulation_mode not in ["historical", "live", "forecast", "scenario"]:
            raise ValueError("Unsupported simulation_mode. Supported values are 'historical', 'live', 'forecast', and 'scenario'.")
        if self.random_seed < 0:
            raise ValueError("random_seed must be a non-negative integer")
    
    @property
    def duration(self) -> timedelta:
        """Calculate the duration of the simulation."""
        return self.end_time - self.start_time
    
    @property
    def duration_minutes(self) -> float:
        """Calculate the duration of the simulation in minutes."""
        return self.duration.total_seconds() / 60
    
    @property
    def total_intervals(self) -> int:
        """Calculate the number of complete simulation intervals."""
        return int(self.duration_minutes // self.interval_minutes)
    
    @property
    def total_measurements(self) -> int:
        """Return one generated measurement per complete simulation interval."""
        return self.total_intervals + 1

    @property
    def effective_end_time(self) -> datetime:
        """Return the last valid timestamp based on complete simulation intervals."""
        return self.start_time + timedelta(minutes=self.total_intervals * self.interval_minutes)
    
    @property
    def effective_duration(self) -> timedelta:
        """Return the duration covered by complete simulation intervals."""
        return self.effective_end_time - self.start_time
    
@dataclass(frozen=True)
class SimulationAsset:
    """Represent an existing database asset used by the simulation."""

    asset_id: int
    asset_code: str
    asset_role: str
    asset_type: str

    region_id: int
    region_code: str

    rated_power_kw: float
    operating_status: Literal["online", "offline", "maintenance", "fault"]

    is_renewable: bool
    is_weather_dependent: bool
    is_dispatchable: bool
    can_store_energy: bool


@dataclass(frozen=True)
class SimulationContext:
    """Represent the conditions for one simulation timestamp."""

    config: SimulationConfig
    current_time: datetime

    random_generator: Random

    # Placeholder multipliers used until real weather and demand data are integrated.
    # A value of 1.0 means no adjustment to the base profile.
    solar_factor: float = 1.0
    wind_factor: float = 1.0
    load_factor: float = 1.0

@dataclass
class SimulationState:
    """Store mutable values that change during a simulation run."""

    last_power_kw_by_asset: dict[int, float] = field(default_factory=dict)
    state_of_charge_percent_by_asset: dict[int, float] = field(default_factory=dict)
    generated_measurement_count: int = 0

@dataclass(frozen=True)
class SimulationMeasurementDraft:
    """Represent a simulated measurement before database persistence."""

    asset_id: int
    measurement_time: datetime
    interval_minutes: int
    active_power_kw: float

    energy_kwh: float | None = None
    source: Literal["simulation"] = "simulation"
    quality_status: Literal["valid", "invalid"] = "valid"