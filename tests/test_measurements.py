import pytest
# ============================================================
# Tests for GET /measurement Endpoint
# ============================================================

def test_get_measurements(client):
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

def test_get_measurements_with_limit(client):
    response = client.get("/measurements?limit=5")

    assert response.status_code == 200

    data = response.json()

    assert len(data) <= 5

@pytest.mark.validation
def test_get_measurements_with_limit_zero_returns_422(client):
    response = client.get("/measurements?limit=0")

    assert response.status_code == 422

@pytest.mark.validation
def test_get_measurements_with_limit_above_max_returns_422(client):

    response = client.get("/measurements?limit=101")

    assert response.status_code == 422

@pytest.mark.validation
def test_get_measurements_with_invalid_type_returns_422(client):
    response = client.get("/measurements?limit=abc")

    assert response.status_code == 422

def test_get_measurements_of_station_id(client):
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

def test_get_measurement_of_station_id_not_found_returns_404(client):
    response = client.get("/stations/9999/measurements")

    assert response.status_code == 404

    assert response.json() == {"detail": "Station with id 9999 not found"}

@pytest.mark.validation
def test_get_measurements_of_station_id_with_invalid_type_returns_422(client):
    response = client.get("/stations/1/measurements?limit=abc")

    assert response.status_code == 422

@pytest.mark.validation
def test_get_measurements_of_station_id_with_limit_zero_returns_422(client):
    response = client.get("/stations/1/measurements?limit=0")

    assert response.status_code == 422

# ============================================================
# Tests for POST /measurement Endpoint
# ============================================================
@pytest.mark.post
def test_post_measurement_returns_201(client, valid_measurement_payload):

    new_measurement = valid_measurement_payload.copy()
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
    
@pytest.mark.post
def test_post_measurement_with_unknown_station_returns_404(client, valid_measurement_payload):
    
    new_measurement = valid_measurement_payload.copy()
    new_measurement["station_id"] = 9999

    response = client.post("/measurements", json=new_measurement)

    assert response.status_code == 404

@pytest.mark.post
@pytest.mark.validation
def test_post_measurement_with_missing_field_returns_422(client, valid_measurement_payload):
    
    new_measurement = valid_measurement_payload.copy()
    del new_measurement["source"]

    response = client.post("/measurements", json=new_measurement)

    assert response.status_code == 422

@pytest.mark.post
@pytest.mark.validation
def test_post_measurement_negative_load_returns_422(client, valid_measurement_payload):
    
    new_measurement = valid_measurement_payload.copy()
    new_measurement["load_value"] = -123.45

    response = client.post("/measurements", json=new_measurement)

    assert response.status_code == 422

@pytest.mark.post
@pytest.mark.validation
def test_post_measurement_invalid_quality_status_returns_422(client, valid_measurement_payload):
    
    new_measurement = valid_measurement_payload.copy()
    new_measurement["quality_status"] = "invalid_status"


    response = client.post("/measurements", json=new_measurement)

    assert response.status_code == 422

@pytest.mark.post
@pytest.mark.validation
def test_post_measurement_empty_source_returns_422(client, valid_measurement_payload):
    
    new_measurement = valid_measurement_payload.copy()
    new_measurement["source"] = ""

    response = client.post("/measurements", json=new_measurement)

    assert response.status_code == 422

@pytest.mark.post
@pytest.mark.validation
def test_post_measurement_invalid_unit_returns_422(client, valid_measurement_payload):
    
    new_measurement = valid_measurement_payload.copy()
    new_measurement["unit"] = "kWh"

    response = client.post("/measurements", json=new_measurement)

    assert response.status_code == 422

# ============================================================
# Tests for GET /measurements/{measurement_id} Endpoint
# ============================================================
@pytest.mark.post
def test_post_measurement_can_be_read_after_creation(client, valid_measurement_payload):
    new_measurement = valid_measurement_payload.copy()
    new_measurement["station_id"] = 8
    new_measurement["load_value"] = 150.00
    new_measurement["quality_status"] = "invalid"

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

def test_get_measurement_by_id_not_found_returns_404(client):
    response = client.get("/measurements/99999999")

    assert response.status_code == 404

    assert response.json() == {"detail": "Measurement with id 99999999 not found"}

@pytest.mark.validation
def test_get_measurement_by_id_with_invalid_range_returns_422(client):
    response = client.get("/measurements/0")

    assert response.status_code == 422

@pytest.mark.validation
def test_get_measurement_by_id_with_invalid_type_returns_422(client):
    response = client.get("/measurements/abc")

    assert response.status_code == 422

# ============================================================
# Tests for PATCH /measurements/{measurement_id} Endpoint
# ============================================================
@pytest.mark.patch
def test_patch_measurement_quality_status_persists_update(client, valid_measurement_payload):
    new_measurement = valid_measurement_payload.copy()
    new_measurement["station_id"] = 7
    new_measurement["quality_status"] = "valid"
    new_measurement["source"] = "pytest PATCH"

    response = client.post("/measurements", json=new_measurement)
    assert response.status_code == 201

    data_post = response.json()

    measurement_id = data_post["measurement_id"]
    new_quality_status = {"quality_status": "invalid"}
    response = client.patch(f"/measurements/{measurement_id}", json=new_quality_status)

    assert response.status_code == 200

    response = client.get(f"/measurements/{measurement_id}")

    assert response.status_code == 200

    data_get = response.json()

    assert data_get["measurement_id"] == measurement_id
    assert data_get["station_id"] == data_post["station_id"]
    assert data_get["measurement_time"] == data_post["measurement_time"]
    assert data_get["load_value"] == data_post["load_value"]
    assert data_get["unit"] == data_post["unit"]
    assert data_get["source"] == data_post["source"]
    assert data_get["quality_status"] == "invalid"

@pytest.mark.patch
def test_patch_measurement_quality_status_not_found_returns_404(client):
    measurement_id = 999999
    new_quality_status = {"quality_status": "invalid"}

    response = client.patch(f"/measurements/{measurement_id}", json=new_quality_status)

    assert response.status_code == 404

@pytest.mark.patch
@pytest.mark.validation
def test_patch_measurement_quality_status_with_missing_status_returns_422(client):
    measurement_id = 5
    new_quality_status = {}

    response = client.patch(f"/measurements/{measurement_id}", json=new_quality_status)

    assert response.status_code == 422

@pytest.mark.patch
@pytest.mark.validation
def test_patch_measurement_quality_status_with_invalid_type_returns_422(client):
    measurement_id = 5
    new_quality_status = {"quality_status": 2}

    response = client.patch(f"/measurements/{measurement_id}", json=new_quality_status)

    assert response.status_code == 422

@pytest.mark.patch
@pytest.mark.validation
def test_patch_measurement_quality_status_with_invalid_status_returns_422(client):
    measurement_id = 5
    new_quality_status = {"quality_status": "wrong_status"}

    response = client.patch(f"/measurements/{measurement_id}", json=new_quality_status)

    assert response.status_code == 422

@pytest.mark.patch
@pytest.mark.validation
def test_patch_measurement_quality_status_with_invalid_measurement_id_returns_422(client):
    new_quality_status = {"quality_status": "invalid"}

    response = client.patch("/measurements/abc", json=new_quality_status)

    assert response.status_code == 422
