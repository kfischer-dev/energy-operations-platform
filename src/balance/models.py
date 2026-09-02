from dataclasses import dataclass
from datetime import datetime
from typing import Literal

BalanceQualityStatus = Literal[
    "valid",
    "incomplete",
    "estimated",
    "invalid",
]


@dataclass(frozen=True)
class BalanceInterval:
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
    start_time: datetime
    end_time: datetime

    total_production_energy_kwh: float
    total_consumption_energy_kwh: float
    total_net_energy_kwh: float

    quality_status: BalanceQualityStatus


@dataclass(frozen=True)
class EnergyMixContribution:
    asset_type: str
    energy_kwh: float
    share_percent: float
    asset_count: int


@dataclass(frozen=True)
class EnergyMix:
    start_time: datetime
    end_time: datetime

    asset_role: Literal["producer", "consumer"]

    total_energy_kwh: float
    contributions: tuple[EnergyMixContribution, ...]

    quality_status: BalanceQualityStatus
