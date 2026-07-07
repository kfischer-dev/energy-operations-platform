import pytest
# ============================================================
# Tests for GET /kpis/measurements Endpoint
# ============================================================
@pytest.mark.kpi
def test_get_measurement_kpi_summary_returns_exact_values(client, reset_db):
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
# Tests for GET stations/{station_id}/kpis Endpoint
# ============================================================
@pytest.mark.kpi
def test_get_station_kpi_summary_returns_kpis(client, reset_db):
    response = client.get("/stations/1/kpis")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)
    assert len(data) > 0
    assert data["measurement_count"] == 3
    assert data["station_id"] == 1
    assert data["station_name"] == "Station A"
    assert float(data["average_load"]) == pytest.approx(92.5)
    assert float(data["min_load"]) == pytest.approx(80.5)
    assert float(data["max_load"]) == pytest.approx(101.75)
    assert data["latest_measurement_time"] is not None 

@pytest.mark.kpi
def test_get_station_kpis_without_measurements_returns_empty_kpis(client, reset_db):
    response = client.get("/stations/9/kpis")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)
    assert data["station_id"] == 9
    assert data["station_name"] == "Station Z"
    assert data["measurement_count"] == 0
    assert data["average_load"] is None
    assert data["min_load"] is None
    assert data["max_load"] is None
    assert data["latest_measurement_time"] is None

@pytest.mark.kpi
def test_get_station_kpis_not_found_returns_404(client):
    response = client.get("/stations/9999/kpis")

    assert response.status_code == 404

    assert response.json() == {"detail": "Station with id 9999 not found"}

@pytest.mark.kpi
@pytest.mark.validation
def test_get_station_kpis_with_invalid_range_returns_422(client):
    response = client.get("/stations/0/kpis")

    assert response.status_code == 422

@pytest.mark.kpi
@pytest.mark.validation
def test_get_station_kpis_with_invalid_type_returns_422(client):
    response = client.get("/stations/abc/kpis")

    assert response.status_code == 422

@pytest.mark.kpi
def test_get_station_kpi_summary_excludes_invalid_measurements(client, reset_db):
    response = client.get("/stations/4/kpis")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)
    assert len(data) > 0
    assert data["measurement_count"] == 1
    assert data["station_id"] == 4
    assert data["station_name"] == "Station D"
    assert float(data["average_load"]) == pytest.approx(25)
    assert float(data["min_load"]) == pytest.approx(25)
    assert float(data["max_load"]) == pytest.approx(25)
    assert data["latest_measurement_time"] is not None 