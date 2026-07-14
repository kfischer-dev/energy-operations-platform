import pytest

# ============================================================
# Asset endpoint tests
# ============================================================
# These tests cover basic asset reads, filtering, 404 behavior, and validation.
# They use the seeded asset data but do not rely on exact KPI calculations.


def test_get_assets(client):
    """Check that the asset list returns records with the expected fields."""

    response = client.get("/assets")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0

    first_asset = data[0]

    assert "asset_id" in first_asset
    assert "asset_name" in first_asset
    assert "asset_code" in first_asset
    assert "asset_location" in first_asset
    assert "asset_role" in first_asset
    assert "asset_type" in first_asset
    assert "region_id" in first_asset
    assert "region_code" in first_asset
    assert "region_name" in first_asset
    assert "rated_power_kw" in first_asset
    assert "latitude" in first_asset
    assert "longitude" in first_asset
    assert "operating_status" in first_asset


def test_get_asset_unknown_type_returns_empty_list(client):
    """Check that filtering by an unknown asset type returns no results."""

    response = client.get("/assets?asset_type=unknown")

    assert response.status_code == 200
    assert response.json() == []


def test_get_asset_by_id_returns_asset(client):
    """Check that a known asset can be loaded by ID."""

    response = client.get("/assets/1")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)
    assert len(data) > 0
    assert data["asset_id"] == 1
    assert "asset_name" in data
    assert "asset_code" in data
    assert "asset_location" in data
    assert "asset_role" in data
    assert "asset_type" in data
    assert "region_id" in data
    assert "region_code" in data
    assert "region_name" in data
    assert "rated_power_kw" in data
    assert "latitude" in data
    assert "longitude" in data
    assert "operating_status" in data


def test_get_asset_not_found_returns_404(client):
    """Check that unknown asset IDs return 404."""

    response = client.get("/assets/9999")

    assert response.status_code == 404

    assert response.json() == {"detail": "Asset with id 9999 not found"}


@pytest.mark.validation
def test_get_asset_id_with_invalid_range_returns_422(client):
    """Check that asset IDs below the allowed range are rejected."""

    response = client.get("/assets/0")

    assert response.status_code == 422


@pytest.mark.validation
def test_get_asset_id_with_invalid_type_returns_422(client):
    """Check that non-integer asset IDs are rejected."""

    response = client.get("/assets/abc")

    assert response.status_code == 422
