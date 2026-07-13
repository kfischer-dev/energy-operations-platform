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
    assert data["measurement_count"] == 22
    assert float(data["average_load"]) == pytest.approx(259.17)
    assert float(data["min_load"]) == pytest.approx(25)
    assert float(data["max_load"]) == pytest.approx(790.25)
    assert data["latest_measurement_time"] is not None


# ============================================================
# Asset-specific KPI endpoint tests
# ============================================================
# The seed file contains specific asset scenarios:
# - Asset 1 / Asset A has known valid measurements.
# - Asset 4 / Asset D includes invalid measurements that should be ignored.
# - Asset 9 / Asset Z exists but has no measurements.


@pytest.mark.kpi
def test_get_asset_kpi_summary_returns_kpis(client, reset_db):
    """Check that Asset A returns the expected KPI values."""

    response = client.get("/assets/1/kpis")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)
    assert len(data) > 0
    assert data["measurement_count"] == 3
    assert data["asset_id"] == 1
    assert data["asset_name"] == "Asset A"
    assert float(data["average_load"]) == pytest.approx(92.5)
    assert float(data["min_load"]) == pytest.approx(80.5)
    assert float(data["max_load"]) == pytest.approx(101.75)
    assert data["latest_measurement_time"] is not None


@pytest.mark.kpi
def test_get_asset_kpis_without_measurements_returns_empty_kpis(client, reset_db):
    """Check that an asset without measurements returns empty KPI values."""

    response = client.get("/assets/9/kpis")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)
    assert data["asset_id"] == 9
    assert data["asset_name"] == "Asset Z"
    assert data["measurement_count"] == 0
    assert data["average_load"] is None
    assert data["min_load"] is None
    assert data["max_load"] is None
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
    """Check that Asset D KPIs are calculated from valid measurements only."""

    response = client.get("/assets/4/kpis")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)
    assert len(data) > 0
    assert data["measurement_count"] == 1
    assert data["asset_id"] == 4
    assert data["asset_name"] == "Asset D"
    assert float(data["average_load"]) == pytest.approx(25)
    assert float(data["min_load"]) == pytest.approx(25)
    assert float(data["max_load"]) == pytest.approx(25)
    assert data["latest_measurement_time"] is not None
