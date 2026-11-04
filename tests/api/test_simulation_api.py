from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from src import api
from src.simulation.models import SimulationConfig, SimulationRunResult
from src.simulation.service import load_simulation_assets

pytestmark = [pytest.mark.api, pytest.mark.simulation]


@pytest.fixture
def simulation_payload():
    """Use a full 24-hour period outside the seeded measurement range."""

    return {
        "simulation_mode": "historical",
        "start_time": "2026-10-01T00:00:00+02:00",
        "end_time": "2026-10-02T00:00:00+02:00",
        "interval_minutes": 15,
        "random_seed": 42,
    }


def measurement_rows(conn):
    """Snapshot every stored value, including measurements from other sources."""
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM measurements ORDER BY measurement_id")
        return cursor.fetchall()


@pytest.mark.parametrize("interval_minutes", [15, 30, 60])
def test_create_and_fetch_simulation_run(
    reset_db, client, database_connection, simulation_payload, interval_minutes
):
    """Execute each supported interval and retrieve the same persisted metadata."""

    simulation_payload["interval_minutes"] = interval_minutes
    response = client.post("/simulation/runs", json=simulation_payload)

    assert response.status_code == 201
    data = response.json()
    run_id = data["simulation_run_id"]
    assert run_id > 0
    assert data["status"] == "completed"
    for field, value in simulation_payload.items():
        assert data[field] == value
    assert data["created_at"] is not None
    assert data["started_at"] is not None
    assert data["completed_at"] is not None
    assert "measurements" not in data
    assert "power_intervals" not in data

    asset_count = len(load_simulation_assets(database_connection))
    # Point measurements include both period boundaries: N intervals need N + 1 points.
    expected_count = asset_count * (24 * 60 // interval_minutes + 1)
    assert data["generated_measurement_count"] == expected_count
    with database_connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) FROM measurements WHERE simulation_run_id = %s",
            (run_id,),
        )
        assert cursor.fetchone()[0] == expected_count

    fetched = client.get(f"/simulation/runs/{run_id}")
    assert fetched.status_code == 200
    assert fetched.json() == data


@pytest.mark.parametrize(
    "changes",
    [
        # Only historical runs and the three release-supported intervals are allowed.
        {"simulation_mode": "live"},
        {"simulation_mode": "forecast"},
        {"simulation_mode": "scenario"},
        {"interval_minutes": 5},
        {"interval_minutes": 0},
        {"interval_minutes": 20},
        # Reject periods over 24 hours, reversed periods and incomplete intervals.
        {"end_time": "2026-10-02T00:15:00+02:00"},
        {"end_time": "2026-10-01T00:00:00+02:00"},
        {"end_time": "2026-09-30T23:00:00+02:00"},
        {"end_time": "2026-10-01T00:14:00+02:00"},
        {"end_time": "2026-10-01T00:15:01+02:00"},
        # Explicit timezone offsets prevent ambiguous simulation timestamps.
        {"start_time": "invalid"},
        {"start_time": "2026-10-01T00:00:00"},
        {"end_time": "2026-10-02T00:00:00"},
        # Seeds must be actual integers that fit the existing PostgreSQL column.
        {"random_seed": -1},
        {"random_seed": 2_147_483_648},
        {"random_seed": True},
        {"random_seed": 1.5},
        # Unknown options must not silently introduce destructive behavior.
        {"delete_existing": True},
    ],
)
def test_invalid_simulation_is_rejected_before_database_access(
    client, monkeypatch, simulation_payload, changes
):
    """Reject invalid requests before opening a connection or creating a run."""

    connection_factory = MagicMock()
    monkeypatch.setattr(api, "get_connection", connection_factory)
    response = client.post("/simulation/runs", json={**simulation_payload, **changes})
    assert response.status_code == 422
    connection_factory.assert_not_called()


@pytest.mark.parametrize("field", ["start_time", "end_time", "random_seed"])
def test_missing_simulation_configuration_is_rejected(
    client, simulation_payload, field
):
    """Require the period and seed rather than silently choosing simulation inputs."""

    del simulation_payload[field]
    assert client.post("/simulation/runs", json=simulation_payload).status_code == 422


@pytest.mark.parametrize("run_id", [0, -1, "invalid"])
def test_invalid_run_id(client, run_id):
    """Reject nonpositive IDs and nonnumeric path values."""

    assert client.get(f"/simulation/runs/{run_id}").status_code == 422


def test_unknown_run_returns_404(client):
    """Distinguish a valid but missing run ID from an invalid request."""

    response = client.get("/simulation/runs/9223372036854775807")
    assert response.status_code == 404


def test_post_uses_id_returned_by_service(client, monkeypatch, simulation_payload):
    """Fetch the service's exact run ID instead of looking up the newest DB entry."""

    connection = MagicMock()
    monkeypatch.setattr(api, "get_connection", MagicMock(return_value=connection))
    execute = MagicMock(return_value=SimulationRunResult(42, 97, []))
    fetch = MagicMock(
        return_value={
            **simulation_payload,
            "simulation_run_id": 42,
            "generated_measurement_count": 97,
            "status": "completed",
            "created_at": simulation_payload["start_time"],
        }
    )
    monkeypatch.setattr(api, "execute_simulation_run", execute)
    monkeypatch.setattr(api, "fetch_simulation_run_by_id", fetch)

    response = client.post("/simulation/runs", json=simulation_payload)

    assert response.status_code == 201
    assert response.json()["simulation_run_id"] == 42
    execute.assert_called_once_with(
        connection,
        SimulationConfig(
            **{
                **simulation_payload,
                "start_time": datetime.fromisoformat(simulation_payload["start_time"]),
                "end_time": datetime.fromisoformat(simulation_payload["end_time"]),
            }
        ),
    )
    fetch.assert_called_once_with(connection, 42)
    connection.close.assert_called_once_with()


@pytest.mark.parametrize("offset_minutes", [0, -15, 30])
def test_overlap_returns_409_and_preserves_all_existing_measurements(
    reset_db, client, database_connection, simulation_payload, offset_minutes
):
    """Rollback conflicting batches while preserving prior measurements and runs."""

    simulation_payload["end_time"] = "2026-10-01T00:30:00+02:00"
    created = client.post("/simulation/runs", json=simulation_payload)
    assert created.status_code == 201
    before = measurement_rows(database_connection)

    # Cover identical periods, a partial overlap and a shared boundary timestamp.
    # The -15-minute case inserts a new point before colliding, testing batch rollback.
    start = datetime.fromisoformat(simulation_payload["start_time"])
    simulation_payload.update(
        start_time=(start + timedelta(minutes=offset_minutes)).isoformat(),
        end_time=(start + timedelta(minutes=offset_minutes + 30)).isoformat(),
    )
    conflict = client.post("/simulation/runs", json=simulation_payload)
    assert conflict.status_code == 409
    assert measurement_rows(database_connection) == before
    assert (
        client.get(f"/simulation/runs/{created.json()['simulation_run_id']}").json()
        == created.json()
    )

    # The failed run remains available for inspection despite its rolled-back data.
    with database_connection.cursor() as cursor:
        cursor.execute(
            "SELECT simulation_run_id FROM simulation_runs WHERE status = 'failed'"
        )
        failed_ids = [row[0] for row in cursor.fetchall()]
    assert len(failed_ids) == 1
    failed = client.get(f"/simulation/runs/{failed_ids[0]}")
    assert failed.status_code == 200
    assert failed.json()["status"] == "failed"
    assert failed.json()["generated_measurement_count"] == 0
    assert failed.json()["completed_at"] is not None


def test_concurrent_overlapping_runs_have_one_winner(
    reset_db, database_connection, simulation_payload
):
    """Concurrent submissions must persist one batch and reject the other with 409."""

    simulation_payload["end_time"] = "2026-10-01T00:30:00+02:00"
    before = measurement_rows(database_connection)

    def submit():
        # Each request uses its own client and application database connection.
        with TestClient(api.app) as client:
            return client.post("/simulation/runs", json=simulation_payload)

    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(executor.map(lambda _: submit(), range(2)))

    assert sorted(response.status_code for response in responses) == [201, 409]
    winner = next(
        response.json() for response in responses if response.status_code == 201
    )
    after = measurement_rows(database_connection)
    assert after[: len(before)] == before
    assert len(after) == len(before) + winner["generated_measurement_count"]


def test_run_statuses_are_returned_from_storage(reset_db, client, database_connection):
    """Return stored lifecycle states, including runs that have not completed."""

    # Set states explicitly because synchronous POST normally finishes before GET.
    for state in ["created", "running", "failed"]:
        with database_connection.cursor() as cursor:
            cursor.execute(
                "UPDATE simulation_runs SET status = %s WHERE simulation_run_id = 1",
                (state,),
            )
        database_connection.commit()
        response = client.get("/simulation/runs/1")
        assert response.status_code == 200
        assert response.json()["status"] == state
