# ============================================================
# General endpoint tests
# ============================================================
# These endpoints should be fast and independent from database content.


def test_health_returns_ok(client):
    """Check that the health endpoint reports the API as available."""

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_home(client):
    """Check that the root endpoint returns the public API message."""

    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Energy Operations Platform API"}
