from fastapi.testclient import TestClient

from src.api import app


client = TestClient(app)

def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Energy Operations Platform API"}

def test_get_stations():
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

def test_get_station_unknown_type_returns_empty_list():
    response = client.get("/stations?station_type=unknown")

    assert response.status_code == 200
    assert response.json() == []

def test_get_station_by_id_returns_station():
    response = client.get("/stations/1")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)
    assert len(data) > 0
    assert data["station_id"] == 1
    assert "station_name" in data
    assert "station_type" in data
    assert "station_location" in data

def test_get_station_not_found_returns_404():
    response = client.get("/stations/9999")

    assert response.status_code == 404

    assert response.json() == {"detail": "Station with id 9999 not found"}

def test_get_station_id_with_invalid_range_returns_422():
    response = client.get("/stations/0")

    assert response.status_code == 422

def test_get_station_id_with_invalid_type_returns_422():
    response = client.get("/stations/abc")

    assert response.status_code == 422

def test_get_measurements():
    response = client.get("/measurements")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0

    first_measurement = data[0]

    assert "station_name" in first_measurement
    assert "measurement_time" in first_measurement
    assert "load_value" in first_measurement
    assert "unit" in first_measurement

def test_get_measurements_with_limit():
    response = client.get("/measurements?limit=5")

    assert response.status_code == 200

    data = response.json()

    assert len(data) <= 5

def test_get_measurements_with_limit_zero_returns_422():
    response = client.get("/measurements?limit=0")

    assert response.status_code == 422

def test_get_measurements_with_limit_above_max_returns_422():

    response = client.get("/measurements?limit=101")

    assert response.status_code == 422

def test_get_measurements_with_invalid_type_returns_422():
    response = client.get("/measurements?limit=abc")

    assert response.status_code == 422

def test_get_measurements_of_station_id():
    response = client.get("/stations/1/measurements")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0

    first_measurement = data[0]

    assert "station_name" in first_measurement
    assert "measurement_time" in first_measurement
    assert "load_value" in first_measurement
    assert "unit" in first_measurement

def test_get_measurement_of_station_id_not_found_returns_404():
    response = client.get("/stations/9999/measurements")

    assert response.status_code == 404

    assert response.json() == {"detail": "Station with id 9999 not found"}

def test_get_measurements_of_station_id_with_invalid_type_returns_422():
    response = client.get("/stations/1/measurements?limit=abc")

    assert response.status_code == 422

def test_get_measurements_of_station_id_with_limit_zero_returns_422():
    response = client.get("/stations/1/measurements?limit=0")

    assert response.status_code == 422

def test_create_measurement_returns_201():

    new_measurement = {
        "station_id": 1,
        "measurement_time": "2026-07-02T08:15:00",
        "load_value": 123.45,
        "unit": "kW",
        "source": "pytest",
        "quality_status": "test",
    }

    response = client.post("/measurements", json=new_measurement)

    assert response.status_code == 201

    data = response.json()

    assert "measurement_id" in data
    assert data["station_id"] == 1
    assert data["load_value"] == 123.45
    assert data["unit"] == "kW"
    assert data["source"] == "pytest"
    assert data["quality_status"] == "test"
    

def test_create_measurement_with_unknown_station_returns_404():
    
    new_measurement = {
        "station_id": 9999,
        "measurement_time": "2026-07-02T08:15:00",
        "load_value": 123.45,
        "unit": "kW",
        "source": "pytest",
        "quality_status": "test",
    }

    response = client.post("/measurements", json=new_measurement)

    assert response.status_code == 404

def test_create_measurement_with_missing_field_returns_422():
    
    new_measurement = {
        "station_id": 1,
        "measurement_time": "2026-07-02T08:15:00",
        "load_value": 123.45,
        "source": "pytest",
        "quality_status": "test",
    }

    response = client.post("/measurements", json=new_measurement)

    assert response.status_code == 422