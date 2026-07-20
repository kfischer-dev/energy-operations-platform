import os

from pathlib import Path


# Always point the application to the dedicated test database before it is imported.
os.environ["DB_NAME"] = "energy_operations_test"

# Safety guard: never allow the test reset helper to run against another database.
if os.environ["DB_NAME"] != "energy_operations_test":
    raise RuntimeError("Refusing to reset non-test database")

import pytest
from fastapi.testclient import TestClient

from src.api import app
from src.database import get_connection

from random import Random
from src.simulation import default_data
from datetime import datetime


def reset_test_database():
    """Reload the test database from the SQL seed file."""

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
    """Start every test session from a known database state."""

    reset_test_database()


@pytest.fixture
def reset_db():
    """Reset the database for tests that need exact seed data."""

    reset_test_database()


@pytest.fixture
def client():
    """Create a FastAPI test client for endpoint tests."""

    return TestClient(app)


@pytest.fixture
def valid_measurement_payload():
    """Base payload for measurement creation tests."""

    return {
        "asset_id": 1,
        "measurement_time": "2026-07-02T08:15:00+02:00",
        "interval_minutes": 15,
        "active_power_kw": 82000.0,
        "energy_kwh": 20500.0,
        "source": "pytest",
        "quality_status": "valid",
    }

@pytest.fixture
def daylight_factor_payload():
    # Sunrise at 06:30 AM in minutes
    sunrise_minutes = 390
    # Peak at 12:30 PM in minutes
    peak_minutes = 750
    # Sunset at 06:30 PM in minutes
    sunset_minutes = 1110

    return sunrise_minutes, peak_minutes, sunset_minutes

@pytest.fixture
def engine_payload(request):
    """Build config, asset, context and profile data for one asset type."""
    asset_type = request.param
    config = default_data.create_default_simulation_config()
    random_generator = Random(config.random_seed)

    if asset_type == "solar_park":
        asset = default_data.create_default_solar_asset()

        context = default_data.create_default_solar_context(
            config=config,
            current_time=datetime(2026, 7, 16, 12, 30),
            random_generator=random_generator,
        )

        profile_data = {
            "solar_park": {
                "sunrise_minutes": 390,
                "peak_minutes": 750,
                "sunset_minutes": 1110,
            }
        }

    elif asset_type == "wind_park":
        asset = default_data.create_default_wind_park_asset()

        context = default_data.create_default_wind_park_context(
            config=config,
            current_time=datetime(2026, 7, 16, 12, 30),
            random_generator=random_generator,
        )

        profile_data = {"wind_park": {}}

    elif asset_type == "hydro_power_plant":
        asset = default_data.create_default_hydro_plant_asset()

        context = default_data.create_default_hydro_plant_context(
            config=config,
            current_time=datetime(2026, 7, 16, 12, 30),
            random_generator=random_generator,
        )

        profile_data = {"hydro_power_plant": {}}

    elif asset_type == "biomass_power_plant":
        asset = default_data.create_default_biomass_asset()

        context = default_data.create_default_biomass_context(
            config=config,
            current_time=datetime(2026, 7, 16, 12, 30),
            random_generator=random_generator,
        )

        profile_data = {"biomass_power_plant": {}}

    else:
        raise ValueError(f"Unsupported asset type: {asset_type}")

    return {
    "config": config,
    "asset": asset,
    "context": context,
    "profile_data": profile_data,
    }
