from dataclasses import replace
from datetime import datetime

import pytest

from src.measurements.models import PowerIntervalDraft
from src.simulation.simulation import validate_complete_interval

INTERVAL_START = datetime(2026, 7, 28, 10, 0)
INTERVAL_END = datetime(2026, 7, 28, 10, 15)


@pytest.fixture
def complete_draft() -> PowerIntervalDraft:
    """Return one complete interval that may be returned."""

    return PowerIntervalDraft(
        asset_id=1,
        interval_start=INTERVAL_START,
        interval_end=INTERVAL_END,
        avg_active_power_kw=120_000.0,
        energy_kwh=30_000.0,
        quality_status="valid",
        aggregation_method="time_weighted_average",
        source_measurement_count=2,
        valid_measurement_count=2,
        coverage_ratio=1.0,
    )


@pytest.mark.validation
def test_validate_complete_interval_accepts_complete_draft(
    complete_draft: PowerIntervalDraft,
) -> None:
    """Accept a complete interval without raising an exception."""

    validate_complete_interval(complete_draft)


@pytest.mark.validation
@pytest.mark.parametrize(
    ("changes", "expected_message"),
    [
        (
            {"quality_status": "incomplete"},
            "Invalid simulation quality status detected.",
        ),
        (
            {"avg_active_power_kw": None},
            "Invalid average active power value detected.",
        ),
        (
            {"avg_active_power_kw": -1.0},
            "Invalid average active power value detected.",
        ),
        (
            {"energy_kwh": None},
            "Invalid energy value detected.",
        ),
        (
            {"energy_kwh": -1.0},
            "Invalid energy value detected.",
        ),
        (
            {"coverage_ratio": 0.5},
            "Incomplete simulation interval detected.",
        ),
    ],
    ids=[
        "invalid-quality-status",
        "missing-power",
        "negative-power",
        "missing-energy",
        "negative-energy",
        "incomplete-coverage",
    ],
)
def test_validate_complete_interval_rejects_invalid_draft(
    complete_draft: PowerIntervalDraft,
    changes: dict[str, object],
    expected_message: str,
) -> None:
    """Reject intervals that do not satisfy complete interval requirements."""

    invalid_draft = replace(complete_draft, **changes)

    with pytest.raises(ValueError, match=expected_message):
        validate_complete_interval(invalid_draft)
