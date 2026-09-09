"""Domain models for portfolio energy balance calculations."""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

BalanceQualityStatus = Literal[
    "valid",
    "incomplete",
    "estimated",
    "invalid",
]

AssetRole = Literal["producer", "consumer", "storage", "grid"]


@dataclass(frozen=True)
class BalanceAsset:
    """Asset metadata required by balance calculations."""

    asset_role: AssetRole
    asset_type: str


@dataclass(frozen=True)
class BalanceInterval:
    """Aggregated production, consumption, and net values for one time window."""

    interval_start: datetime
    interval_end: datetime

    avg_production_power_kw: float
    avg_consumption_power_kw: float
    avg_net_power_kw: float

    production_energy_kwh: float
    consumption_energy_kwh: float
    net_energy_kwh: float

    quality_status: BalanceQualityStatus


@dataclass(frozen=True)
class BalanceSummary:
    """Energy totals and overall quality for a requested analysis period."""

    start_time: datetime
    end_time: datetime

    total_production_energy_kwh: float
    total_consumption_energy_kwh: float
    total_net_energy_kwh: float

    quality_status: BalanceQualityStatus


@dataclass(frozen=True)
class EnergyMixContribution:
    """Energy contribution of one asset type within an energy mix."""

    asset_type: str
    energy_kwh: float
    share_percent: float
    asset_count: int


@dataclass(frozen=True)
class EnergyMix:
    """Energy distribution by asset type for one role over a time period."""

    start_time: datetime
    end_time: datetime

    asset_role: Literal["producer", "consumer"]

    total_energy_kwh: float
    contributions: tuple[EnergyMixContribution, ...]

    quality_status: BalanceQualityStatus


@dataclass(frozen=True)
class EnergyMixItem:
    """Energy contribution of one asset type within an energy mix for a specific role."""

    asset_type: str
    energy_kwh: float
    share_percent: float
