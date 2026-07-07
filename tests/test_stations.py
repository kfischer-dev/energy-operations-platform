import pytest
# ============================================================
# Tests for GET /station Endpoints
# ============================================================

def test_get_stations(client):
    response = client.get("/stations")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0

    first_station = data[0]

    assert "station_id" in first_station
    assert "station_name" in first_station
    assert "station_type" in first_station
    assert "station_location" in first_station

def test_get_station_unknown_type_returns_empty_list(client):
    response = client.get("/stations?station_type=unknown")

    assert response.status_code == 200
    assert response.json() == []

def test_get_station_by_id_returns_station(client):
    response = client.get("/stations/1")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)
    assert len(data) > 0
    assert data["station_id"] == 1
    assert "station_name" in data
    assert "station_type" in data
    assert "station_location" in data

def test_get_station_not_found_returns_404(client):
    response = client.get("/stations/9999")

    assert response.status_code == 404

    assert response.json() == {"detail": "Station with id 9999 not found"}

@pytest.mark.validation
def test_get_station_id_with_invalid_range_returns_422(client):
    response = client.get("/stations/0")

    assert response.status_code == 422

@pytest.mark.validation
def test_get_station_id_with_invalid_type_returns_422(client):
    response = client.get("/stations/abc")

    assert response.status_code == 422