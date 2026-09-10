import pytest
from fastapi.testclient import TestClient

from src.api import app


@pytest.mark.api
@pytest.mark.cors
def test_cors_headers():
    client = TestClient(app)

    response = client.options(
        "/assets",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == (
        "http://localhost:5173"
    )
    assert "GET" in response.headers.get("access-control-allow-methods", "")
