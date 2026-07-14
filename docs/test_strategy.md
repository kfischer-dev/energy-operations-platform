# Test Strategy

## Purpose

This document describes the automated testing approach of the Energy Operations Platform in `v0.10.0`.

The goal is a test suite that is understandable, deterministic and safe for database-backed API development without hiding the underlying behavior behind excessive test infrastructure.

Related documentation:

- [`api_reference.md`](api_reference.md)
- [`database_notes.md`](database_notes.md)
- [`data_dictionary.md`](data_dictionary.md)

## Current Scope

The suite contains **40 tests** across four modules:

| Module | Tests | Main scope |
|---|---:|---|
| `tests/test_general.py` | 2 | root and health endpoints |
| `tests/test_assets.py` | 6 | asset summaries, details, filtering, 404 and validation |
| `tests/test_measurements.py` | 24 | list/detail reads, limits, POST, PATCH, persistence and validation |
| `tests/test_kpis.py` | 8 | global and asset KPIs, invalid/estimated filtering and empty scenarios |

## Test Stack

- `pytest`
- FastAPI `TestClient`
- dedicated PostgreSQL test database
- shared fixtures in `tests/conftest.py`
- deterministic SQL seed data
- marker-based targeted runs

## Dedicated Test Database

Tests use:

```text
energy_operations_test
```

Before importing the application, `tests/conftest.py` sets:

```python
os.environ["DB_NAME"] = "energy_operations_test"
```

A safety guard rejects database resets when the configured name is not exactly the expected test database.

The test database must already contain the current schema. The reset helper reloads data but does not execute `schema.sql`.

## Shared Fixtures

### `setup_test_database`

Session-scoped and automatic.

Purpose:

- reset the test dataset once before the test session,
- provide a known starting state.

### `reset_db`

Function-scoped and opt-in.

Purpose:

- restore deterministic seed values before tests that need exact aggregate results,
- remove changes introduced by earlier write tests.

### `client`

Creates a FastAPI `TestClient` for API requests.

### `valid_measurement_payload`

Provides a valid 15-minute measurement request used as the base for POST and PATCH workflows.

## Test Data Strategy

The suite uses three data strategies.

### 1. Deterministic seed scenarios

Use for:

- exact KPI calculations,
- known assets with specific quality states,
- assets without measurements,
- read-only domain scenarios.

Important stable scenarios:

| Asset ID | Scenario |
|---:|---|
| `1` | three valid wind measurements |
| `4` | battery storage with storage specifications |
| `5` | two invalid negatives plus one valid measurement |
| `7` | two valid plus one estimated measurement |
| `8` | substation measurements |
| `9` | asset without measurements |

### 2. Test-created records

Use for:

- successful POST behavior,
- create-then-read persistence,
- create-then-PATCH persistence.

These tests create the exact record they need and use returned IDs rather than relying on fixed measurement IDs.

### 3. Request-only scenarios

Use for:

- invalid path and query types,
- invalid ranges,
- missing fields,
- unsupported literal values,
- clearly non-existing IDs.

## Reset Rules

Use `reset_db` when:

- an exact KPI result depends on the original seed state,
- the test asserts counts, averages, sums or latest timestamps,
- earlier writes could affect the expected result.

Do not use `reset_db` automatically for every test when:

- only response structure is checked,
- the test creates its own isolated data,
- the result is independent of the current row count,
- the test checks request validation before database work.

The current compromise keeps the suite fast and explicit while protecting exact analytics tests.

## Current Test Areas

### General endpoints

- root message
- API health response

### Asset endpoints

- compact asset-list contract
- complete asset-detail contract
- exact asset-type filtering
- unknown asset returns `404`
- invalid asset ID range/type returns `422`

### Measurement reads

- compact summary contract
- global list limit
- asset-specific measurement list
- missing parent asset returns `404`
- measurement detail not-found and validation behavior

### Measurement creation

- valid request returns `201`
- complete detail response after creation
- unknown parent asset returns `404`
- missing required field returns `422`
- invalid quality status returns `422`
- empty source returns `422`
- created measurement can be read back

### Measurement update

- quality status can be patched
- update persists and can be read back
- unknown measurement returns `404`
- missing, invalid or unsupported quality status returns `422`
- invalid measurement ID type returns `422`

### KPI behavior

- exact global valid-only KPIs
- exact asset KPIs
- existing asset without measurements returns zero/null values
- unknown asset returns `404`
- invalid and estimated measurements are excluded
- exact total interval energy is asserted

## Response Contract Tests

List tests verify that summary responses remain compact. For example, measurement summaries must not expose:

```text
asset_type
asset_role
region_code
interval_minutes
source
```

Detail, POST and PATCH responses use the complete `MeasurementResponse`, including `asset_type`. Tests protect the public name from accidentally leaking the internal database field name `asset_type_name`.

## KPI Assertions

Exact KPI tests assert:

- `measurement_count`
- `average_power_kw`
- `min_power_kw`
- `max_power_kw`
- `total_energy_kwh`
- non-null or null `latest_measurement_time`

`pytest.approx()` is used for numeric comparisons where appropriate.

## Markers

Configured markers:

| Marker | Purpose |
|---|---|
| `post` | measurement creation tests |
| `patch` | measurement update tests |
| `kpi` | analytics and KPI tests |
| `validation` | requests expected to return `422` |

Targeted execution:

```bash
py -m pytest -v -m post
py -m pytest -v -m patch
py -m pytest -v -m kpi
py -m pytest -v -m validation
```

## Recommended Execution Order During Development

Run the smallest relevant group first:

```bash
py -m pytest tests/test_measurements.py -v
py -m pytest tests/test_kpis.py -v
py -m pytest tests/test_assets.py -v
py -m pytest -v
```

Before a release, always run the complete suite from a freshly seeded test database.

## Practical Rules for New Tests

- Tests must not depend on execution order.
- Successful write tests should use unique asset/timestamp combinations.
- Use returned resource IDs instead of guessing identity values.
- Keep 404 IDs clearly outside the seed range.
- Exact analytics tests must request `reset_db`.
- Validation tests should change only the field relevant to the scenario.
- Summary and detail contracts should be tested separately.
- Add a dedicated test whenever a new quality state affects analytics.

## Known Trade-offs

- The database is reset through SQL rather than transaction rollback.
- Some read-only tests rely on the session-level seed state.
- The test schema must be updated manually after schema changes.
- Tests currently require a reachable local PostgreSQL instance.
- Docker-based or CI-based test execution is not implemented yet.

## Next Test Improvements

1. Add automated schema initialization for the test database.
2. Add CI execution through GitHub Actions.
3. Consider transaction rollback or per-module database isolation.
4. Add direct tests for region and storage endpoints when those APIs exist.
5. Add simulation property tests once generated time series are introduced.
6. Add database constraint tests for duplicate timestamps and invalid storage ranges.
