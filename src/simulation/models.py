from dataclasses import dataclass, field
from datetime import datetime, timedelta
from random import Random
from typing import Literal

# ============================================================
# Simulation Configuration
# ============================================================


@dataclass(frozen=True)
class SimulationConfig:
    """Stores validated configuration settings for measurement simulations."""

    start_time: datetime
    end_time: datetime
    interval_minutes: int
    random_seed: int
    simulation_mode: Literal["historical", "live", "forecast", "scenario"]

    def __post_init__(self) -> None:
        """Validates the simulation configuration after initialization."""

        if self.start_time >= self.end_time:
            raise ValueError("start_time must be before end_time")

        if self.interval_minutes not in [5, 15, 30, 60]:
            raise ValueError(
                "Unsupported interval_minutes. Supported values are 5, 15, 30, and 60."
            )

        if self.simulation_mode not in [
            "historical",
            "live",
            "forecast",
            "scenario",
        ]:
            raise ValueError(
                "Unsupported simulation_mode. Supported values are "
                "'historical', 'live', 'forecast', and 'scenario'."
            )

        if self.random_seed < 0:
            raise ValueError("random_seed must be a non-negative integer")

    @property
    def duration(self) -> timedelta:
        """Returns the configured simulation duration."""

        return self.end_time - self.start_time

    @property
    def duration_minutes(self) -> float:
        """Returns the configured simulation duration in minutes."""

        return self.duration.total_seconds() / 60

    @property
    def total_intervals(self) -> int:
        """Returns the number of complete simulation intervals."""

        return int(self.duration_minutes // self.interval_minutes)

    @property
    def total_grid_points(self) -> int:
        """Returns the number of timestamps required for all complete intervals."""

        return self.total_intervals + 1

    @property
    def effective_end_time(self) -> datetime:
        """Returns the final timestamp covered by complete intervals."""

        return self.start_time + timedelta(
            minutes=self.total_intervals * self.interval_minutes
        )

    @property
    def effective_duration(self) -> timedelta:
        """Returns the duration covered by complete simulation intervals."""

        return self.effective_end_time - self.start_time


# ============================================================
# Simulation Domain Models
# ============================================================


@dataclass(frozen=True)
class SimulationAsset:
    """Represents an existing database asset used by the simulation."""

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
    """Represents the conditions for one simulation timestamp."""

    config: SimulationConfig
    current_time: datetime
    random_generator: Random

    # Temporary multipliers until real weather and demand data are integrated.
    # A value of 1.0 leaves the corresponding base profile unchanged.
    solar_factor: float = 1.0
    wind_factor: float = 1.0
    load_factor: float = 1.0
    hydro_factor: float = 1.0
    biomass_factor: float = 1.0


@dataclass
class SimulationState:
    """Stores mutable values that change during a simulation run."""

    last_power_kw_by_asset: dict[int, float] = field(default_factory=dict)
    state_of_charge_percent_by_asset: dict[int, float] = field(default_factory=dict)
    generated_measurement_count: int = 0
