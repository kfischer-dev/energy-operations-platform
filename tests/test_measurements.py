import pytest

# ============================================================
# Measurement read endpoint tests
# ============================================================
# These tests check read behavior and response shape. They do not assert exact
# KPI values, so they can rely on the session-level seed setup.


def test_get_measurements(client):
    """Check that the measurement list returns records with the expected fields."""

    response = client.get("/measurements")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0

    first_measurement = data[0]

    assert "asset_name" in first_measurement
    assert "measurement_time" in first_measurement
    assert "load_value" in first_measurement
    assert "unit" in first_measurement


def test_get_measurements_with_limit(client):
    """Check that the limit query parameter restricts the number of results."""

    response = client.get("/measurements?limit=5")

    assert response.status_code == 200

    data = response.json()

    assert len(data) <= 5


@pytest.mark.validation
def test_get_measurements_with_limit_zero_returns_422(client):
    """Check that a limit below the allowed range is rejected."""

    response = client.get("/measurements?limit=0")

    assert response.status_code == 422


@pytest.mark.validation
def test_get_measurements_with_limit_above_max_returns_422(client):
    """Check that a limit above the allowed range is rejected."""

    response = client.get("/measurements?limit=101")

    assert response.status_code == 422


@pytest.mark.validation
def test_get_measurements_with_invalid_type_returns_422(client):
    """Check that non-integer limit values are rejected."""

    response = client.get("/measurements?limit=abc")

    assert response.status_code == 422


def test_get_measurements_of_asset_id(client):
    """Check that measurements can be listed for a known asset."""

    response = client.get("/assets/1/measurements")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0

    first_measurement = data[0]

    assert "asset_name" in first_measurement
    assert "measurement_time" in first_measurement
    assert "load_value" in first_measurement
    assert "unit" in first_measurement


def test_get_measurement_of_asset_id_not_found_returns_404(client):
    """Check that measurement requests for unknown assets return 404."""

    response = client.get("/assets/9999/measurements")

    assert response.status_code == 404

    assert response.json() == {"detail": "Asset with id 9999 not found"}


@pytest.mark.validation
def test_get_measurements_of_asset_id_with_invalid_type_returns_422(client):
    """Check that non-integer limit values are rejected for asset measurements."""

    response = client.get("/assets/1/measurements?limit=abc")

    assert response.status_code == 422


@pytest.mark.validation
def test_get_measurements_of_asset_id_with_limit_zero_returns_422(client):
    """Check that too small limit values are rejected for asset measurements."""

    response = client.get("/assets/1/measurements?limit=0")

    assert response.status_code == 422


# ============================================================
# Measurement create endpoint tests
# ============================================================
# POST tests start from a valid payload and change only the field that matters
# for the scenario. Successful POST tests create their own measurement records.


@pytest.mark.post
def test_post_measurement_returns_201(client, valid_measurement_payload):
    """Check that a valid measurement can be created for an existing asset."""

    new_measurement = valid_measurement_payload.copy()
    new_measurement["asset_id"] = 8
    new_measurement["load_value"] = 105.25

    response = client.post("/measurements", json=new_measurement)

    assert response.status_code == 201

    data = response.json()

    assert "measurement_id" in data
    assert data["asset_id"] == 8
    assert data["load_value"] == 105.25
    assert data["unit"] == "kW"
    assert data["source"] == "pytest"
    assert data["quality_status"] == "valid"


@pytest.mark.post
def test_post_measurement_with_unknown_asset_returns_404(client, valid_measurement_payload):
    """Check that measurements cannot be created for unknown assets."""

    new_measurement = valid_measurement_payload.copy()
    new_measurement["asset_id"] = 9999

    response = client.post("/measurements", json=new_measurement)

    assert response.status_code == 404


@pytest.mark.post
@pytest.mark.validation
def test_post_measurement_with_missing_field_returns_422(client, valid_measurement_payload):
    """Check that payloads with missing required fields are rejected."""

    new_measurement = valid_measurement_payload.copy()
    del new_measurement["source"]

    response = client.post("/measurements", json=new_measurement)

    assert response.status_code == 422


@pytest.mark.post
@pytest.mark.validation
def test_post_measurement_negative_load_returns_422(client, valid_measurement_payload):
    """Check that negative load values are rejected."""

    new_measurement = valid_measurement_payload.copy()
    new_measurement["load_value"] = -123.45

    response = client.post("/measurements", json=new_measurement)

    assert response.status_code == 422


@pytest.mark.post
@pytest.mark.validation
def test_post_measurement_invalid_quality_status_returns_422(client, valid_measurement_payload):
    """Check that unsupported quality_status values are rejected."""

    new_measurement = valid_measurement_payload.copy()
    new_measurement["quality_status"] = "invalid_status"

    response = client.post("/measurements", json=new_measurement)

    assert response.status_code == 422


@pytest.mark.post
@pytest.mark.validation
def test_post_measurement_empty_source_returns_422(client, valid_measurement_payload):
    """Check that empty source values are rejected."""

    new_measurement = valid_measurement_payload.copy()
    new_measurement["source"] = ""

    response = client.post("/measurements", json=new_measurement)

    assert response.status_code == 422


@pytest.mark.post
@pytest.mark.validation
def test_post_measurement_invalid_unit_returns_422(client, valid_measurement_payload):
    """Check that unsupported measurement units are rejected."""

    new_measurement = valid_measurement_payload.copy()
    new_measurement["unit"] = "kWh"

    response = client.post("/measurements", json=new_measurement)

    assert response.status_code == 422


# ============================================================
# Measurement detail endpoint tests
# ============================================================


@pytest.mark.post
def test_post_measurement_can_be_read_after_creation(client, valid_measurement_payload):
    """Check that a newly created measurement can be read back by ID."""

    new_measurement = valid_measurement_payload.copy()
    new_measurement["asset_id"] = 8
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
    assert data_get["asset_id"] == data_post["asset_id"]
    assert data_get["measurement_time"] == data_post["measurement_time"]
    assert data_get["load_value"] == data_post["load_value"]
    assert data_get["unit"] == data_post["unit"]
    assert data_get["source"] == data_post["source"]
    assert data_get["quality_status"] == data_post["quality_status"]


def test_get_measurement_by_id_not_found_returns_404(client):
    """Check that unknown measurement IDs return 404."""

    response = client.get("/measurements/99999999")

    assert response.status_code == 404

    assert response.json() == {"detail": "Measurement with id 99999999 not found"}


@pytest.mark.validation
def test_get_measurement_by_id_with_invalid_range_returns_422(client):
    """Check that measurement IDs below the allowed range are rejected."""

    response = client.get("/measurements/0")

    assert response.status_code == 422


@pytest.mark.validation
def test_get_measurement_by_id_with_invalid_type_returns_422(client):
    """Check that non-integer measurement IDs are rejected."""

    response = client.get("/measurements/abc")

    assert response.status_code == 422


# ============================================================
# Measurement update endpoint tests
# ============================================================
# PATCH tests only update quality_status. The persistence test creates its own
# measurement first, so it does not depend on a measurement ID from the seed file.


@pytest.mark.patch
def test_patch_measurement_quality_status_persists_update(client, valid_measurement_payload):
    """Check that a quality_status update is saved and can be read back."""

    new_measurement = valid_measurement_payload.copy()
    new_measurement["asset_id"] = 7
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
    assert data_get["asset_id"] == data_post["asset_id"]
    assert data_get["measurement_time"] == data_post["measurement_time"]
    assert data_get["load_value"] == data_post["load_value"]
    assert data_get["unit"] == data_post["unit"]
    assert data_get["source"] == data_post["source"]
    assert data_get["quality_status"] == "invalid"


@pytest.mark.patch
def test_patch_measurement_quality_status_not_found_returns_404(client):
    """Check that updating an unknown measurement returns 404."""

    measurement_id = 999999
    new_quality_status = {"quality_status": "invalid"}

    response = client.patch(f"/measurements/{measurement_id}", json=new_quality_status)

    assert response.status_code == 404


@pytest.mark.patch
@pytest.mark.validation
def test_patch_measurement_quality_status_with_missing_status_returns_422(client):
    """Check that PATCH requires a quality_status field."""

    measurement_id = 5
    new_quality_status = {}

    response = client.patch(f"/measurements/{measurement_id}", json=new_quality_status)

    assert response.status_code == 422


@pytest.mark.patch
@pytest.mark.validation
def test_patch_measurement_quality_status_with_invalid_type_returns_422(client):
    """Check that non-string quality_status values are rejected."""

    measurement_id = 5
    new_quality_status = {"quality_status": 2}

    response = client.patch(f"/measurements/{measurement_id}", json=new_quality_status)

    assert response.status_code == 422


@pytest.mark.patch
@pytest.mark.validation
def test_patch_measurement_quality_status_with_invalid_status_returns_422(client):
    """Check that unsupported quality_status values are rejected."""

    measurement_id = 5
    new_quality_status = {"quality_status": "wrong_status"}

    response = client.patch(f"/measurements/{measurement_id}", json=new_quality_status)

    assert response.status_code == 422


@pytest.mark.patch
@pytest.mark.validation
def test_patch_measurement_quality_status_with_invalid_measurement_id_returns_422(client):
    """Check that non-integer measurement IDs are rejected."""

    new_quality_status = {"quality_status": "invalid"}

    response = client.patch("/measurements/abc", json=new_quality_status)

    assert response.status_code == 422
