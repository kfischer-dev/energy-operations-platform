from datetime import datetime

import pytest

from src.balance.repository import fetch_balance_measurements
from src.balance.service import build_balance_series, build_balance_summary
from src.database import fetch_asset_summaries


@pytest.mark.smoke
@pytest.mark.balance
def test_build_balance_summary_from_db_measurements(
    reset_db,
    database_connection,
):
    start_time = datetime.fromisoformat("2026-06-22T10:00:00+02:00")
    end_time = datetime.fromisoformat("2026-06-22T10:30:00+02:00")

    measurements = fetch_balance_measurements(
        conn=database_connection,
        start_time=start_time,
        end_time=end_time,
    )

    database_assets = fetch_asset_summaries(database_connection)

    balance_series = build_balance_series(
        measurements=measurements,
        database_assets=database_assets,
        start_time=start_time,
        end_time=end_time,
        interval_minutes=15,
    )

    balance_summary = build_balance_summary(balance_series)

    assert balance_summary.total_production_energy_kwh == pytest.approx(92_875.0)
    assert balance_summary.total_consumption_energy_kwh == pytest.approx(124_375.0)
    assert balance_summary.total_net_energy_kwh == pytest.approx(-31_500.0)

    assert balance_summary.total_net_energy_kwh == pytest.approx(
        balance_summary.total_production_energy_kwh
        - balance_summary.total_consumption_energy_kwh
    )
