from dataclasses import replace
from pathlib import Path

import psycopg
import pytest

from src.database import get_connection
from src.simulation.default_data import create_default_simulation_config
from src.simulation.repository import create_simulation_run, fetch_simulation_run_by_id

pytestmark = [pytest.mark.integration, pytest.mark.repository, pytest.mark.scenarios]


@pytest.fixture
def isolated_run_table():
    """Use the actual schema in a temporary table; never reset or write real tables."""
    schema = (Path(__file__).resolve().parents[2] / "sql" / "schema.sql").read_text(
        encoding="utf-8"
    )
    definition = schema.split("CREATE TABLE simulation_runs (", 1)[1].split("\n);", 1)[
        0
    ]
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("CREATE TEMP TABLE simulation_runs (" + definition + "\n);")
            cursor.execute("SET LOCAL search_path = pg_temp")
        yield conn
    finally:
        conn.rollback()
        conn.close()


@pytest.mark.parametrize(
    "scenario", ["baseline", "cloudy_day", "windy_day", "high_demand", "energy_stress"]
)
def test_scenario_round_trip(isolated_run_table, scenario):
    config = replace(create_default_simulation_config(), scenario=scenario)
    run_id = create_simulation_run(isolated_run_table, config)

    run = fetch_simulation_run_by_id(isolated_run_table, run_id)

    assert run["simulation_run_id"] == run_id
    assert run["scenario"] == scenario
    assert run["simulation_mode"] == config.simulation_mode
    assert run["status"] == "created"


def test_database_default_and_scenario_constraints(isolated_run_table):
    conn = isolated_run_table
    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO simulation_runs
                (simulation_mode, start_time, end_time, interval_minutes, status)
            VALUES ('historical', '2026-01-01', '2026-01-02', 15, 'created')
            RETURNING scenario
            """
        )
        assert cursor.fetchone()[0] == "baseline"

    # Savepoints isolate each expected constraint failure without affecting the table.
    for scenario, error in [
        ("invalid", psycopg.errors.CheckViolation),
        (None, psycopg.errors.NotNullViolation),
    ]:
        with pytest.raises(error), conn.transaction(), conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO simulation_runs
                    (simulation_mode, start_time, end_time, interval_minutes, status, scenario)
                VALUES ('historical', '2026-01-01', '2026-01-02', 15, 'created', %s)
                """,
                (scenario,),
            )
