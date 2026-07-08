import pytest

# ============================================================
# Station endpoint tests
# ============================================================
# These tests cover basic station reads, filtering, 404 behavior, and validation.
# They use the seeded station data but do not rely on exact KPI calculations.


def test_get_stations(client):
    """Check that the station list returns records with the expected fields."""

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
    """Check that filtering by an unknown station type returns no results."""

    response = client.get("/stations?station_type=unknown")

    assert response.status_code == 200
    assert response.json() == []


def test_get_station_by_id_returns_station(client):
    """Check that a known station can be loaded by ID."""

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
    """Check that unknown station IDs return 404."""

    response = client.get("/stations/9999")

    assert response.status_code == 404

    assert response.json() == {"detail": "Station with id 9999 not found"}


@pytest.mark.validation
def test_get_station_id_with_invalid_range_returns_422(client):
    """Check that station IDs below the allowed range are rejected."""

    response = client.get("/stations/0")

    assert response.status_code == 422


@pytest.mark.validation
def test_get_station_id_with_invalid_type_returns_422(client):
    """Check that non-integer station IDs are rejected."""

    response = client.get("/stations/abc")

    assert response.status_code == 422
