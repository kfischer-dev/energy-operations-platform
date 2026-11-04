"""Fixed scenario multipliers for the existing power profiles.

Factors apply to the profile's calculated power, not directly to context factors.
This keeps wind variation intact and allows the result to be capped at rated power.
"""

from dataclasses import dataclass, fields
from math import isfinite
from types import MappingProxyType
from typing import Literal

ScenarioName = Literal[
    "baseline", "cloudy_day", "windy_day", "high_demand", "energy_stress"
]
ProfileKind = Literal["solar", "wind", "load", "hydro", "biomass"]


@dataclass(frozen=True)
class ScenarioFactors:
    """Non-negative, finite multipliers applied to calculated profile power."""

    solar: float = 1.0
    wind: float = 1.0
    load: float = 1.0
    hydro: float = 1.0
    biomass: float = 1.0

    def __post_init__(self) -> None:
        for factor in fields(self):
            value = getattr(self, factor.name)
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not isfinite(value)
                or not 0 <= value <= 2
            ):
                raise ValueError(
                    f"{factor.name} factor must be finite and between 0 and 2"
                )

    def scale_power(
        self, profile: ProfileKind, power_kw: float, rated_power_kw: float
    ) -> float:
        """Scale valid profile power without exceeding the asset's rated power."""

        if profile not in {"solar", "wind", "load", "hydro", "biomass"}:
            raise ValueError(f"Unknown profile kind: {profile}")
        if (
            not isfinite(power_kw)
            or not isfinite(rated_power_kw)
            or rated_power_kw < 0
            or not 0 <= power_kw <= rated_power_kw
        ):
            raise ValueError("Profile power must be finite and within rated power")
        return min(power_kw * getattr(self, profile), rated_power_kw)


SCENARIOS = MappingProxyType(
    {
        "baseline": ScenarioFactors(),
        "cloudy_day": ScenarioFactors(solar=0.4),
        "windy_day": ScenarioFactors(wind=1.2),
        "high_demand": ScenarioFactors(load=1.15),
        "energy_stress": ScenarioFactors(solar=0.4, wind=0.5, load=1.15),
    }
)


def get_scenario(name: ScenarioName) -> ScenarioFactors:
    """Return one of the five fixed scenario definitions."""

    try:
        return SCENARIOS[name]
    except KeyError as error:
        raise ValueError(f"Unknown simulation scenario: {name}") from error
