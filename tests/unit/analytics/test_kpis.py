import pytest

# ============================================================
# Global KPI endpoint tests
# ============================================================
# Exact KPI tests depend on the fixed seed state from sql/test_seed_data.sql.
# reset_db keeps these calculations stable even if other tests create or update data.


@pytest.mark.kpi
def test_get_measurement_kpi_summary_returns_exact_values(client, reset_db):
    """Check the global KPI summary against the known seed data."""

    response = client.get("/kpis/measurements")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)
    assert len(data) > 0
    assert data["measurement_count"] == 21
    assert float(data["average_power_kw"]) == pytest.approx(65500)
    assert float(data["min_power_kw"]) == pytest.approx(8000)
    assert float(data["max_power_kw"]) == pytest.approx(149000)
    assert float(data["total_energy_kwh"]) == pytest.approx(343875)
    assert data["latest_measurement_time"] is not None


# ============================================================
# Asset-specific KPI endpoint tests
# ============================================================
# The seed file contains specific asset scenarios:
# - Asset 1 has known valid measurements.
# - Asset 5 includes invalid measurements that should be ignored.
# - Asset 7 includes one estimated measurement that should be ignored.
# - Asset 9 exists but has no measurements.


@pytest.mark.kpi
def test_get_asset_kpi_summary_returns_kpis(client, reset_db):
    """Check that Asset 1 returns the expected KPI values."""

    response = client.get("/assets/1/kpis")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)
    assert len(data) > 0
    assert data["measurement_count"] == 3
    assert data["asset_id"] == 1
    assert data["asset_name"] == "Test Wind Park North Sea"
    assert float(data["average_power_kw"]) == pytest.approx(81000)
    assert float(data["min_power_kw"]) == pytest.approx(79000)
    assert float(data["max_power_kw"]) == pytest.approx(84000)
    assert float(data["total_energy_kwh"]) == pytest.approx(60750)
    assert data["latest_measurement_time"] is not None


@pytest.mark.kpi
def test_get_asset_kpis_without_measurements_returns_empty_kpis(client, reset_db):
    """Check that an asset without measurements returns empty KPI values."""

    response = client.get("/assets/9/kpis")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)
    assert data["asset_id"] == 9
    assert data["asset_name"] == "Test Asset Without Measurements"
    assert data["measurement_count"] == 0
    assert data["average_power_kw"] is None
    assert data["min_power_kw"] is None
    assert data["max_power_kw"] is None
    assert data["total_energy_kwh"] is None
    assert data["latest_measurement_time"] is None


@pytest.mark.kpi
def test_get_asset_kpis_not_found_returns_404(client):
    """Check that KPI requests for unknown assets return 404."""

    response = client.get("/assets/9999/kpis")

    assert response.status_code == 404

    assert response.json() == {"detail": "Asset with id 9999 not found"}


@pytest.mark.kpi
@pytest.mark.validation
def test_get_asset_kpis_with_invalid_range_returns_422(client):
    """Check that asset IDs below the allowed range are rejected."""

    response = client.get("/assets/0/kpis")

    assert response.status_code == 422


@pytest.mark.kpi
@pytest.mark.validation
def test_get_asset_kpis_with_invalid_type_returns_422(client):
    """Check that non-integer asset IDs are rejected."""

    response = client.get("/assets/abc/kpis")

    assert response.status_code == 422


@pytest.mark.kpi
def test_get_asset_kpi_summary_excludes_invalid_measurements(client, reset_db):
    """Check that Asset 5 KPIs are calculated from valid measurements only."""

    response = client.get("/assets/5/kpis")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)
    assert len(data) > 0
    assert data["measurement_count"] == 1
    assert data["asset_id"] == 5
    assert data["asset_name"] == "Test Industrial Load Stuttgart"
    assert float(data["average_power_kw"]) == pytest.approx(102000)
    assert float(data["min_power_kw"]) == pytest.approx(102000)
    assert float(data["max_power_kw"]) == pytest.approx(102000)
    assert float(data["total_energy_kwh"]) == pytest.approx(25500)
    assert data["latest_measurement_time"] is not None


@pytest.mark.kpi
def test_get_asset_kpi_summary_excludes_estimated_measurements(client, reset_db):
    """Check that Asset 7 KPIs exclude estimated values."""

    response = client.get("/assets/7/kpis")

    assert response.status_code == 200

    data = response.json()

    assert data["asset_id"] == 7
    assert data["asset_name"] == "Test Data Center Rhine-Ruhr"
    assert data["measurement_count"] == 2
    assert float(data["average_power_kw"]) == pytest.approx(62500)
    assert float(data["min_power_kw"]) == pytest.approx(62000)
    assert float(data["max_power_kw"]) == pytest.approx(63000)
    assert float(data["total_energy_kwh"]) == pytest.approx(31250)
    assert data["latest_measurement_time"] is not None
