import pytest

# ============================================================
# Shared KPI period
# ============================================================

START_TIME = "2026-06-22T08:00:00+02:00"
END_TIME = "2026-06-22T08:30:00+02:00"

KPI_PARAMS = {
    "start_time": START_TIME,
    "end_time": END_TIME,
}


# ============================================================
# Global KPI endpoint tests
# ============================================================
# Exact KPI tests depend on the fixed seed state from sql/test_seed_data.sql.
# reset_db keeps these calculations stable even if other tests create or update data.


@pytest.mark.kpi
def test_get_measurement_kpi_summary_returns_exact_values(client, reset_db):
    """Check the global period KPI summary against the known seed data."""

    response = client.get("/kpis/measurements", params=KPI_PARAMS)

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)

    assert data["period_start"] == START_TIME
    assert data["period_end"] == END_TIME

    assert data["measurement_count"] == 21
    assert data["min_measured_power_kw"] == pytest.approx(8000.0)
    assert data["max_measured_power_kw"] == pytest.approx(149000.0)

    assert data["avg_active_power_kw"] == pytest.approx(445848.96, abs=0.01)
    assert data["total_energy_kwh"] == pytest.approx(222924.48, abs=0.01)
    assert data["coverage_ratio"] == pytest.approx(0.875)


# ============================================================
# Asset-specific KPI endpoint tests
# ============================================================
# The seed file contains specific asset scenarios:
# - Asset 1 has valid measurements plus support points around the KPI period.
# - Asset 5 has only one valid measurement in the period.
# - Asset 7 contains one estimated measurement that is excluded.
# - Asset 9 exists but has no measurements.


@pytest.mark.kpi
def test_get_asset_kpi_summary_returns_kpis(client, reset_db):
    """Check that Asset 1 returns the expected period KPI values."""

    response = client.get("/assets/1/kpis", params=KPI_PARAMS)

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)

    assert data["asset_id"] == 1
    assert data["asset_name"] == "Test Wind Park North Sea"

    assert data["period_start"] == START_TIME
    assert data["period_end"] == END_TIME

    assert data["measurement_count"] == 3
    assert data["min_measured_power_kw"] == pytest.approx(79000.0)
    assert data["max_measured_power_kw"] == pytest.approx(84000.0)

    assert data["avg_active_power_kw"] == pytest.approx(81598.96, abs=0.01)
    assert data["total_energy_kwh"] == pytest.approx(40799.48, abs=0.01)
    assert data["coverage_ratio"] == pytest.approx(1.0)


@pytest.mark.kpi
def test_get_asset_kpis_without_measurements_returns_empty_kpis(client, reset_db):
    """Check that an asset without measurements returns empty period KPIs."""

    response = client.get("/assets/9/kpis", params=KPI_PARAMS)

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)

    assert data["asset_id"] == 9
    assert data["asset_name"] == "Test Asset Without Measurements"

    assert data["period_start"] == START_TIME
    assert data["period_end"] == END_TIME

    assert data["measurement_count"] == 0
    assert data["min_measured_power_kw"] is None
    assert data["max_measured_power_kw"] is None
    assert data["avg_active_power_kw"] is None
    assert data["total_energy_kwh"] is None
    assert data["coverage_ratio"] == pytest.approx(0.0)


@pytest.mark.kpi
def test_get_asset_kpis_not_found_returns_404(client):
    """Check that KPI requests for unknown assets return 404."""

    response = client.get("/assets/9999/kpis", params=KPI_PARAMS)

    assert response.status_code == 404
    assert response.json() == {"detail": "Asset with id 9999 not found"}


@pytest.mark.kpi
@pytest.mark.validation
def test_get_asset_kpis_with_invalid_range_returns_422(client):
    """Check that asset IDs below the allowed range are rejected."""

    response = client.get("/assets/0/kpis", params=KPI_PARAMS)

    assert response.status_code == 422


@pytest.mark.kpi
@pytest.mark.validation
def test_get_asset_kpis_with_invalid_type_returns_422(client):
    """Check that non-integer asset IDs are rejected."""

    response = client.get("/assets/abc/kpis", params=KPI_PARAMS)

    assert response.status_code == 422


@pytest.mark.kpi
@pytest.mark.validation
def test_get_asset_kpis_with_invalid_period_returns_422(client):
    """Check that KPI periods with end_time before start_time are rejected."""

    response = client.get(
        "/assets/1/kpis",
        params={
            "start_time": END_TIME,
            "end_time": START_TIME,
        },
    )

    assert response.status_code == 422
    assert response.json() == {"detail": "end_time must be after start_time"}


@pytest.mark.kpi
def test_get_asset_kpi_summary_excludes_invalid_measurements(client, reset_db):
    """Keep measured KPIs but skip interval KPIs when only one valid point remains."""

    response = client.get("/assets/5/kpis", params=KPI_PARAMS)

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)

    assert data["asset_id"] == 5
    assert data["asset_name"] == "Test Industrial Load Stuttgart"

    assert data["measurement_count"] == 1
    assert data["min_measured_power_kw"] == pytest.approx(102000.0)
    assert data["max_measured_power_kw"] == pytest.approx(102000.0)

    assert data["avg_active_power_kw"] is None
    assert data["total_energy_kwh"] is None
    assert data["coverage_ratio"] == pytest.approx(0.0)


@pytest.mark.kpi
def test_get_asset_kpi_summary_excludes_estimated_measurements(client, reset_db):
    """Check that Asset 7 KPIs exclude estimated values."""

    response = client.get("/assets/7/kpis", params=KPI_PARAMS)

    assert response.status_code == 200

    data = response.json()

    assert data["asset_id"] == 7
    assert data["asset_name"] == "Test Data Center Rhine-Ruhr"

    assert data["measurement_count"] == 2
    assert data["min_measured_power_kw"] == pytest.approx(62000.0)
    assert data["max_measured_power_kw"] == pytest.approx(63000.0)

    assert data["avg_active_power_kw"] == pytest.approx(62500.0)
    assert data["total_energy_kwh"] == pytest.approx(31250.0)
    assert data["coverage_ratio"] == pytest.approx(1.0)
