import pytest

# ============================================================
# Balance endpoint tests
# ============================================================


@pytest.mark.api
@pytest.mark.balance
def test_get_balance_summary(client):
    """Check that the balance summary endpoint returns the expected fields."""

    response = client.get(
        "/balance",
        params={
            "start_time": "2026-06-22T10:00:00+02:00",
            "end_time": "2026-06-22T10:30:00+02:00",
            "interval_minutes": 15,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)

    assert data["start_time"] == "2026-06-22T10:00:00+02:00"
    assert data["end_time"] == "2026-06-22T10:30:00+02:00"

    assert data["total_production_energy_kwh"] == pytest.approx(92_875.0)
    assert data["total_consumption_energy_kwh"] == pytest.approx(124_375.0)
    assert data["total_net_energy_kwh"] == pytest.approx(-31_500.0)

    assert data["quality_status"] == "valid"


@pytest.mark.api
@pytest.mark.balance
def test_get_balance_series(client):
    """Check that the balance series endpoint returns the expected fields."""

    response = client.get(
        "/balance/series",
        params={
            "start_time": "2026-06-22T10:00:00+02:00",
            "end_time": "2026-06-22T10:30:00+02:00",
            "interval_minutes": 15,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0

    first_interval = data[0]

    assert first_interval["interval_start"] == "2026-06-22T10:00:00+02:00"
    assert first_interval["interval_end"] == "2026-06-22T10:15:00+02:00"

    assert first_interval["avg_production_power_kw"] == pytest.approx(183_500.0)
    assert first_interval["avg_consumption_power_kw"] == pytest.approx(246_000.0)
    assert first_interval["avg_net_power_kw"] == pytest.approx(-62_500.0)

    assert first_interval["production_energy_kwh"] == pytest.approx(45_875.0)
    assert first_interval["consumption_energy_kwh"] == pytest.approx(61_500.0)
    assert first_interval["net_energy_kwh"] == pytest.approx(-15_625.0)

    assert first_interval["quality_status"] == "valid"

    second_interval = data[1]

    assert second_interval["interval_start"] == "2026-06-22T10:15:00+02:00"
    assert second_interval["interval_end"] == "2026-06-22T10:30:00+02:00"

    assert second_interval["avg_production_power_kw"] == pytest.approx(188_000.0)
    assert second_interval["avg_consumption_power_kw"] == pytest.approx(251_500.0)
    assert second_interval["avg_net_power_kw"] == pytest.approx(-63_500.0)

    assert second_interval["production_energy_kwh"] == pytest.approx(47_000.0)
    assert second_interval["consumption_energy_kwh"] == pytest.approx(62_875.0)
    assert second_interval["net_energy_kwh"] == pytest.approx(-15_875.0)

    assert second_interval["quality_status"] == "valid"


@pytest.mark.api
@pytest.mark.balance
def test_get_balance_rejects_invalid_time_period(client):
    """Check that the balance endpoint rejects an invalid time period."""

    response = client.get(
        "/balance",
        params={
            "start_time": "2026-06-22T10:30:00+02:00",
            "end_time": "2026-06-22T10:00:00+02:00",
            "interval_minutes": 15,
        },
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "end_time must be after start_time"
    }
