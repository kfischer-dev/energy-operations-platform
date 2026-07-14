# Version History

This document tracks the main implementation and learning milestones of the Energy Operations Platform.

The project uses small, explainable versions so the GitHub history shows how the platform evolved from Python fundamentals into a domain-oriented backend.

## Current Version

| Version | Status | Summary |
|---|---|---|
| `v0.10.0` | current | Introduced the energy-domain foundation with regions, asset types, enriched assets, interval energy, storage specifications, summary/detail API contracts and migrated tests |

## Version Timeline

| Version | Status | Main result | Learning value |
|---|---|---|---|
| `v0.1` | completed | Python dictionaries, first statistics and classification logic | Python syntax, functions and data structures |
| `v0.2` | completed | File handling, TXT/CSV workflows and error handling | File processing and robust data flow |
| `v0.3` | completed | `Asset` class and CSV-to-object workflow | OOP, encapsulation and modules |
| `v0.3.2` | completed | Logging, README and first GitHub-ready structure | Traceability and documentation |
| `v0.4` | completed | PostgreSQL schema, seed data, queries and Python DB access | Relational modeling and DB integration |
| `v0.4.1` | completed | Tuple-to-dictionary database result mapping | JSON and API preparation |
| `v0.5` | completed | First FastAPI app with general, asset and measurement reads | Backend, HTTP and JSON basics |
| `v0.5.1` | completed | Swagger/OpenAPI metadata | API discoverability |
| `v0.5.2` | completed | Pydantic response models | Typed API contracts |
| `v0.5.3` | completed | First pytest/TestClient tests | Automated API testing |
| `v0.6.0` | completed | `POST /measurements` | Insert flow and write API |
| `v0.6.1` | completed | Measurement input validation | Pydantic constraints and 422 behavior |
| `v0.6.2` | completed | Measurement detail endpoint and create/read flow | Resource detail and persistence tests |
| `v0.6.3` | completed | PATCH for measurement quality status | Partial updates and data quality |
| `v0.7.0` | completed | Global measurement KPIs | SQL aggregation and valid-only analytics |
| `v0.7.1` | completed | Asset-specific KPIs | Scoped analytics and empty results |
| `v0.8.0` | completed | Dedicated test database | Environment isolation |
| `v0.8.1` | completed | Deterministic KPI assertions | Stable exact-value tests |
| `v0.8.2` | completed | Improved POST/PATCH test flows | Maintainable write tests |
| `v0.8.3` | completed | pytest markers | Targeted test execution |
| `v0.8.4` | completed | Modular test files and shared fixtures | Test organization |
| `v0.8.5` | completed | Test strategy and documentation split | Clear user/developer documentation |
| `v0.8.6` | completed | Centralized 404 helpers | Reduced API duplication |
| `v0.8` | released | Testing, robustness and API consistency milestone | First portfolio-oriented pre-release |
| `v0.9.0` | completed | Dockerfile and standalone FastAPI image | Container basics and port mapping |
| `v0.9.1` | completed | Compose stack for FastAPI and PostgreSQL | Multi-container networking, volumes and initialization |
| `v0.9.2` | completed | PostgreSQL health check and delayed API startup | Reliable service readiness |
| `v0.10.0` | current | Energy-domain database, API and test migration | Domain modeling, schema evolution, API contracts and energy analytics |

## v0.8 Focus — Testing and Robustness

The `v0.8` milestone established:

- an isolated test database,
- deterministic seed scenarios,
- exact KPI assertions,
- POST/PATCH persistence flows,
- pytest markers,
- modular test files,
- shared fixtures,
- centralized 404 handling,
- clearer documentation boundaries.

## v0.9 Focus — Docker Foundation

The `v0.9.x` series added:

- a FastAPI Docker image,
- a clean build context,
- FastAPI and PostgreSQL Compose services,
- internal hostname `db`,
- persistent database storage,
- automatic first-run schema and seed initialization,
- PostgreSQL health checking,
- API startup after database readiness.

The infrastructure foundation is now sufficient for the portfolio MVP. Further Docker work should follow real deployment needs rather than adding tools for their own sake.

## v0.10.0 — Energy Domain Foundation

### Database and domain model

- replaced the narrow station concept with `assets`,
- added four schematic German regions,
- added reusable `asset_types`,
- introduced producer, consumer, storage and grid roles,
- added renewable, weather-dependent, dispatchable and storage capability flags,
- expanded asset master data with codes, location, rated power, coordinates and operating status,
- replaced generic load/unit fields with `active_power_kw`, `energy_kwh` and `interval_minutes`,
- added one-to-one battery `storage_specs`,
- added realistic development and deterministic test datasets.

### API contracts

- migrated routes and helpers from stations to assets,
- added compact `AssetSummaryResponse` and `MeasurementSummaryResponse`,
- retained rich detail responses for individual resources,
- unified GET detail, POST and PATCH measurement output,
- exposed public `asset_type` consistently while keeping `asset_type_name` internal to the database,
- migrated API descriptions to power and energy terminology.

### Analytics

- renamed load KPIs to active-power KPIs,
- added `total_energy_kwh`,
- retained valid-only analytics,
- explicitly tested exclusion of invalid and estimated measurements,
- preserved empty-KPI behavior for assets without valid rows.

### Testing and cleanup

- migrated all endpoint tests to the asset and energy model,
- added summary-versus-detail contract checks,
- maintained deterministic POST/PATCH flows,
- expanded the suite to 40 tests,
- removed private notes and runtime logs from the release package,
- aligned all focused documentation with the implemented model.

## Documentation Split

| Document | Role |
|---|---|
| `README.md` | concise portfolio entry point and quick start |
| `docs/api_reference.md` | public endpoint and model contracts |
| `docs/data_dictionary.md` | authoritative domain and field definitions |
| `docs/database_notes.md` | schema implementation and DB access layer |
| `docs/test_strategy.md` | test database, fixtures and scenarios |
| `docs/deployment_notes.md` | Docker and local environment |
| `docs/version_history.md` | implementation and learning milestones |

## Next Planned Work

| Planned version/block | Focus |
|---|---|
| `v0.11` | simulation foundation with configurable periods and intervals |
| later simulation patch | producer, consumer, storage and grid profiles |
| weather block | regional weather time series and weather-driven generation |
| analytics block | global and regional energy balance |
| recommendation block | rule-based operational actions |
| frontend phase | React dashboard with map, KPIs, charts and live/history views |
| cloud phase | Azure deployment after the backend MVP is stable |
