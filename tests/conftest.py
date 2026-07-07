import os
from pathlib import Path

os.environ["DB_NAME"] = "energy_operations_test"

if os.environ["DB_NAME"] != "energy_operations_test":
    raise RuntimeError("Refusing to reset non-test database")

import pytest
from fastapi.testclient import TestClient

from src.api import app
from src.database import get_connection


def reset_test_database():
    seed_file = Path(__file__).resolve().parents[1] / "sql" / "test_seed_data.sql"

    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(seed_file.read_text(encoding="utf-8"))
        conn.commit()
    finally:
        conn.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    reset_test_database()

# Reset Database for specific tests
@pytest.fixture
def reset_db():
    reset_test_database()

# Client for test modules
@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def valid_measurement_payload():
    return {
        "station_id": 1,
        "measurement_time": "2026-07-02T08:15:00",
        "load_value": 123.45,
        "unit": "kW",
        "source": "pytest",
        "quality_status": "valid",
    }