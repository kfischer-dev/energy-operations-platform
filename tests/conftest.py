import os
from datetime import datetime
from pathlib import Path
from random import Random

import pytest
from fastapi.testclient import TestClient

# Point the application to the dedicated test database before importing it.
os.environ["DB_NAME"] = "energy_operations_test"

# Safety guard: never allow test resets against another database.
if os.environ["DB_NAME"] != "energy_operations_test":
    raise RuntimeError("Refusing to reset non-test database")

from src.api import app
from src.database import get_connection
from src.simulation import default_data


def reset_test_database() -> None:
    """Reload the test database from the SQL seed file."""

    seed_file = Path(__file__).resolve().parents[1] / "sql" / "test_seed_data.sql"
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(seed_file.read_text(encoding="utf-8"))
        connection.commit()
    finally:
        connection.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_database() -> None:
    """Start every test session from a known database state."""

    reset_test_database()


@pytest.fixture
def reset_db() -> None:
    """Reset the database for tests that require exact seed data."""

    reset_test_database()


@pytest.fixture
def client() -> TestClient:
    """Create a FastAPI test client for endpoint tests."""

    return TestClient(app)


@pytest.fixture
def valid_measurement_payload() -> dict:
    """Return a valid base payload for measurement creation tests."""

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
def daylight_factor_payload() -> tuple[int, int, int]:
    """Return sunrise, peak and sunset times expressed in minutes."""

    sunrise_minutes = 390
    peak_minutes = 750
    sunset_minutes = 1110

    return sunrise_minutes, peak_minutes, sunset_minutes


@pytest.fixture
def engine_payload(request) -> dict:
    """Build config, asset, context and profile data for one asset type."""

    asset_type = request.param
    config = default_data.create_default_simulation_config()
    random_generator = Random(config.random_seed)
    current_time = datetime(2026, 7, 16, 12, 30)

    if asset_type == "solar_park":
        asset = default_data.create_default_solar_asset()
        context = default_data.create_default_solar_context(
            config=config,
            current_time=current_time,
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
            current_time=current_time,
            random_generator=random_generator,
        )
        profile_data = {"wind_park": {}}

    elif asset_type == "hydro_power_plant":
        asset = default_data.create_default_hydro_plant_asset()
        context = default_data.create_default_hydro_plant_context(
            config=config,
            current_time=current_time,
            random_generator=random_generator,
        )
        profile_data = {"hydro_power_plant": {}}

    elif asset_type == "biomass_power_plant":
        asset = default_data.create_default_biomass_asset()
        context = default_data.create_default_biomass_context(
            config=config,
            current_time=current_time,
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
