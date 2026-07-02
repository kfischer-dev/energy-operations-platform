from fastapi.testclient import TestClient

from src.api import app


client = TestClient(app)

# ============================================================
# Payload
# ============================================================

def valid_measurement_payload():
    return {
        "station_id": 1,
        "measurement_time": "2026-07-02T08:15:00",
        "load_value": 123.45,
        "unit": "kW",
        "source": "pytest",
        "quality_status": "valid",
    }

# ============================================================
# Validation test for General Endpoints
# ============================================================

def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Energy Operations Platform API"}

# ============================================================
# Validation test for GET /station Endpoints
# ============================================================

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

# ============================================================
# Validation test for GET /measurement Endpoint
# ============================================================

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

# ============================================================
# Validation test for POST /measurement Endpoint
# ============================================================

def test_create_measurement_returns_201():

    new_measurement = valid_measurement_payload()
    new_measurement["station_id"] = 8
    new_measurement["load_value"] = 105.25

    response = client.post("/measurements", json=new_measurement)

    assert response.status_code == 201

    data = response.json()

    assert "measurement_id" in data
    assert data["station_id"] == 8
    assert data["load_value"] == 105.25
    assert data["unit"] == "kW"
    assert data["source"] == "pytest"
    assert data["quality_status"] == "valid"
    

def test_create_measurement_with_unknown_station_returns_404():
    
    new_measurement = valid_measurement_payload()
    new_measurement["station_id"] = 9999

    response = client.post("/measurements", json=new_measurement)

    assert response.status_code == 404

def test_create_measurement_with_missing_field_returns_422():
    
    new_measurement = valid_measurement_payload()
    del new_measurement["source"]

    response = client.post("/measurements", json=new_measurement)

    assert response.status_code == 422

def test_create_measurement_negative_load_returns_422():
    
    new_measurement = valid_measurement_payload()
    new_measurement["load_value"] = -123.45

    response = client.post("/measurements", json=new_measurement)

    assert response.status_code == 422

def test_create_measurement_invalid_quality_status_returns_422():
    
    new_measurement = valid_measurement_payload()
    new_measurement["quality_status"] = "invalid_status"


    response = client.post("/measurements", json=new_measurement)

    assert response.status_code == 422

def test_create_measurement_empty_source_returns_422():
    
    new_measurement = valid_measurement_payload()
    new_measurement["source"] = ""

    response = client.post("/measurements", json=new_measurement)

    assert response.status_code == 422

def test_create_measurement_invalid_unit_returns_422():
    
    new_measurement = valid_measurement_payload()
    new_measurement["unit"] = "kWh"

    response = client.post("/measurements", json=new_measurement)

    assert response.status_code == 422

# ============================================================
# Validation test for GET /measurements/{measurement_id} Endpoint
# ============================================================

def test_get_measurement_by_id_returns_measurement():

    new_measurement = {
        "station_id": 8,
        "measurement_time": "2026-07-02T10:15:00",
        "load_value": 150.00,
        "unit": "kW",
        "source": "pytest",
        "quality_status": "invalid",
    }

    response_post = client.post("/measurements", json=new_measurement)

    assert response_post.status_code == 201

    data_post = response_post.json()
    measurement_id = data_post["measurement_id"]

    response_get = client.get(f"/measurements/{measurement_id}")

    assert response_get.status_code == 200

    data_get = response_get.json()

    assert data_get["measurement_id"] == measurement_id
    assert data_get["station_id"] == data_post["station_id"]
    assert data_get["measurement_time"] == data_post["measurement_time"]
    assert data_get["load_value"] == data_post["load_value"]
    assert data_get["unit"] == data_post["unit"]
    assert data_get["source"] == data_post["source"]
    assert data_get["quality_status"] == data_post["quality_status"]

def test_get_measurement_by_id_not_found_returns_404():
    response = client.get("/measurements/99999999")

    assert response.status_code == 404

    assert response.json() == {"detail": "Measurement with id 99999999 not found"}

def test_get_measurement_by_id_with_invalid_range_returns_422():
    response = client.get("/measurements/0")

    assert response.status_code == 422


def test_get_measurement_by_id_with_invalid_type_returns_422():
    response = client.get("/measurements/abc")

    assert response.status_code == 422
