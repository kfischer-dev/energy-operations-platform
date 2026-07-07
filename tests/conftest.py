import os
from pathlib import Path

import pytest

os.environ["DB_NAME"] = "energy_operations_test"

if os.environ["DB_NAME"] != "energy_operations_test":
    raise RuntimeError("Refusing to reset non-test database")

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

# ============================================================
# Reset Database for specific tests
# ============================================================
@pytest.fixture
def reset_db():
    reset_test_database()