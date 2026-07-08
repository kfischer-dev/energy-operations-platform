# Test Strategy

This document describes the current testing approach for the Energy Operations Platform.  
It focuses on test data handling, database reset rules, and the separation between seed-based tests, self-contained tests, and validation tests.

## Scope

The current test suite covers:

- General API endpoints
- Station endpoints
- Measurement read endpoints
- Measurement create/update flows
- KPI and analytics endpoints
- Not-found behavior
- Request validation behavior

## Test Database

All automated tests must run against the dedicated test database:

```text
energy_operations_test
```

The test setup explicitly sets the database name before importing the application:

```python
os.environ["DB_NAME"] = "energy_operations_test"
```

A safety check prevents accidental reset operations on a non-test database.

## Test Client

API tests use FastAPI's `TestClient` through the shared `client` fixture.

```python
@pytest.fixture
def client():
    return TestClient(app)
```

This keeps endpoint tests close to real API behavior while avoiding manual server startup.

## Test Data Strategy

The test suite uses three categories of test data.

| Category | Description | Typical use |
|---|---|---|
| Seed-based data | Data loaded from `sql/test_seed_data.sql` | Exact KPI calculations and read-only tests that require a known database state |
| Test-created data | Data created inside the test itself | POST, PATCH, and create-then-read flows |
| Request-only data | Invalid or non-existing request values | 404 and 422 tests where the exact database state is not relevant |

## Database Reset Rules

The test database is reset once at the start of the test session.

```python
@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    reset_test_database()
```

Individual tests should only use the `reset_db` fixture when they require an exact seed state.

### Use `reset_db` when

- the test expects exact KPI values,
- the test depends on a specific seed station,
- the test depends on a specific number of valid measurements,
- the test verifies behavior for a seeded station without measurements.

### Do not use `reset_db` when

- the test creates its own data,
- the test checks request validation,
- the test checks not-found behavior with clearly non-existing IDs,
- the database state does not affect the expected result.

## Current Test Areas

| Test area | Example test | Data source | Fixed IDs? | Requires `reset_db`? | Reason |
|---|---|---|---|---|---|
| General health endpoint | `test_health_returns_ok` | Request-only | No | No | Static endpoint without database dependency |
| General root endpoint | `test_home` | Request-only | No | No | Static endpoint without database dependency |
| Station list | `test_get_stations` | Seed data | No | No | Only checks that a list with station fields is returned |
| Station by ID | `test_get_station_by_id_returns_station` | Seed data | Yes, station `1` | No | Checks one known station; currently stable after session setup |
| Unknown station type | `test_get_station_unknown_type_returns_empty_list` | Request-only | No | No | Checks filter behavior for a non-existing type |
| Station not found | `test_get_station_not_found_returns_404` | Request-only | Yes, non-existing station `9999` | No | Exact seed state is not relevant |
| Station validation | `test_get_station_id_with_invalid_range_returns_422`, `test_get_station_id_with_invalid_type_returns_422` | Request-only | No | No | Checks FastAPI/Pydantic validation |
| Measurement list | `test_get_measurements` | Seed data | No | No | Only checks that data and expected fields exist |
| Measurement list limit | `test_get_measurements_with_limit` | Seed data | No | No | Checks API limit behavior, not exact database content |
| Measurement limit validation | `test_get_measurements_with_limit_zero_returns_422`, `test_get_measurements_with_limit_above_max_returns_422`, `test_get_measurements_with_invalid_type_returns_422` | Request-only | No | No | Checks request validation |
| Measurements by station | `test_get_measurements_of_station_id` | Seed data | Yes, station `1` | No | Checks that station measurements can be returned |
| Measurements by unknown station | `test_get_measurement_of_station_id_not_found_returns_404` | Request-only | Yes, non-existing station `9999` | No | Exact seed state is not relevant |
| Measurement by ID not found | `test_get_measurement_by_id_not_found_returns_404` | Request-only | Yes, non-existing measurement `99999999` | No | Exact seed state is not relevant |
| Measurement ID validation | `test_get_measurement_by_id_with_invalid_range_returns_422`, `test_get_measurement_by_id_with_invalid_type_returns_422` | Request-only | No | No | Checks request validation |
| POST measurement | `test_post_measurement_returns_201` | Test-created data | Uses existing station `8` | No | Verifies create flow and response content |
| POST unknown station | `test_post_measurement_with_unknown_station_returns_404` | Request-only + payload fixture | Yes, non-existing station `9999` | No | Checks foreign-key/business validation behavior |
| POST validation | Missing field, negative load, invalid status, empty source, invalid unit | Request payload | No | No | Checks request validation |
| Create then read | `test_post_measurement_can_be_read_after_creation` | Test-created data | Uses existing station `8` | No | Verifies that created data can be retrieved by ID |
| PATCH measurement | `test_patch_measurement_quality_status_persists_update` | Test-created data | Uses existing station `7` | No | Verifies update flow on a measurement created inside the test |
| PATCH not found | `test_patch_measurement_quality_status_not_found_returns_404` | Request-only | Yes, non-existing measurement `999999` | No | Exact seed state is not relevant |
| PATCH validation | Missing status, invalid type, invalid status, invalid measurement ID | Request payload | No | No | Checks request validation |
| Global KPI | `test_get_measurement_kpi_summary_returns_exact_values` | Seed data | No fixed entity ID, but fixed seed state | Yes | Expects exact aggregate values |
| Station KPI | `test_get_station_kpi_summary_returns_kpis` | Seed data | Yes, station `1` | Yes | Expects exact KPI values for Station A |
| Station without measurements KPI | `test_get_station_kpis_without_measurements_returns_empty_kpis` | Seed data | Yes, station `9` | Yes | Expects Station Z to have no measurements |
| Station KPI excludes invalid measurements | `test_get_station_kpi_summary_excludes_invalid_measurements` | Seed data | Yes, station `4` | Yes | Verifies that invalid measurements are excluded from KPI calculations |
| Station KPI not found | `test_get_station_kpis_not_found_returns_404` | Request-only | Yes, non-existing station `9999` | No | Exact seed state is not relevant |
| Station KPI validation | Invalid range/type for station KPI endpoint | Request-only | No | No | Checks request validation |

## Current Markers

The test suite currently uses markers to group selected tests.

| Marker | Purpose |
|---|---|
| `kpi` | KPI and analytics related tests |
| `post` | Measurement creation tests |
| `patch` | Measurement update tests |
| `validation` | Request validation tests expecting `422 Unprocessable Entity` |

## Guidelines for New Tests

When adding a new test, decide first which data strategy it needs.

### Prefer test-created data when

- the test checks create/update behavior,
- the test needs a specific measurement,
- the test should not depend on the global seed state.

### Prefer seed data when

- the test checks a known read-only scenario,
- the test checks exact KPI values,
- the test needs a stable station with known measurements.

### Prefer request-only tests when

- the test checks validation,
- the test checks not-found behavior,
- no real database content is required for the expected result.

## Practical Rules

- Tests must not depend on execution order.
- `reset_db` should be used deliberately, not automatically.
- KPI tests with exact expected values should use `reset_db`.
- POST and PATCH tests should create the data they need.
- Validation tests should remain independent of database content.
- Tests should use clearly non-existing IDs for 404 cases.
- Seed data should remain stable and documented when exact KPI assertions depend on it.

## Known Trade-off

Some read-only tests currently rely on the session-level seed setup without calling `reset_db` individually. This is acceptable as long as these tests do not assert exact aggregate values and do not depend on data changed by previous tests.

If test instability appears later, the next improvement should be a more isolated test data strategy, for example:

- resetting the database per test module,
- using transaction rollback per test,
- creating dedicated fixtures for stations and measurements,
- separating read-only seed tests from write tests more strictly.

## Summary

The current strategy is intentionally simple:

- Use a dedicated test database.
- Load a known seed state at the beginning of the test session.
- Reset only when exact seed-dependent assertions require it.
- Let create/update tests generate their own data.
- Keep validation and not-found tests independent from database state.

This keeps the test suite understandable, fast enough for local development, and suitable for the current portfolio stage.
