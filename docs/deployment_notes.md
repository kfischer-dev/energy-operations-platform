# Deployment Notes

## Purpose

This document describes the local containerized environment and developer execution paths of the Energy Operations Platform in `v0.12.0`.

The Docker foundation was established in `v0.9.x`. `v0.12.0` keeps the same container architecture and point-in-time measurement schema; the release extends simulation behavior with consumer profiles and does not require a new service or table.

Related documentation:

- [`database_notes.md`](database_notes.md)
- [`api_reference.md`](api_reference.md)
- [`test_strategy.md`](test_strategy.md)

---

# Current Stack

```text
Host browser / API client
        |
        | localhost:8000
        v
FastAPI container
        |
        | DB_HOST=db:5432
        v
PostgreSQL 18 container
```

Current capabilities:

- FastAPI image built from the project `Dockerfile`,
- PostgreSQL 18 service,
- internal Compose service networking,
- PostgreSQL readiness health check,
- API startup only after the database is healthy,
- automatic schema and development seed initialization for a new volume,
- persistent PostgreSQL data through `db_data`,
- host API access on port `8000`,
- optional host database access on port `5433`,
- simulation-run and raw-power persistence supported by the same database.

---

# Services

## `api`

The API service:

- builds from the local `Dockerfile`,
- exposes `8000:8000`,
- reads `.env`,
- overrides `DB_HOST` with Compose service name `db`,
- depends on a healthy PostgreSQL service,
- starts Uvicorn on `0.0.0.0:8000`.

## `db`

The database service:

- uses `postgres:18`,
- reads `POSTGRES_USER`, `POSTGRES_PASSWORD` and `POSTGRES_DB`,
- exposes host port `5433` to container port `5432`,
- stores data in the named volume `db_data`,
- initializes `schema.sql` and `seed_data.sql` only for a new data directory,
- reports readiness through `pg_isready`.

---

# Dockerfile

Current build sequence:

1. Base image: `python:3.14-slim`
2. Working directory: `/app`
3. Copy `requirements.txt`
4. Install Python dependencies
5. Copy project files
6. Expose port `8000`
7. Start Uvicorn

Container command:

```bash
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

`0.0.0.0` is required so the host can reach Uvicorn through Docker port mapping.

---

# Environment Variables

Create `.env` from `.env.example`.

Base example:

```env
# FastAPI database connection
DB_NAME=energy_operations
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=5432

# PostgreSQL container initialization
POSTGRES_DB=energy_operations
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here
```

## Inside Compose

Compose overrides:

```text
DB_HOST=db
```

Container-to-container PostgreSQL endpoint:

```text
host: db
port: 5432
```

## Host process connecting to Docker PostgreSQL

Because Compose maps:

```text
5433:5432
```

use:

```text
DB_HOST=localhost
DB_PORT=5433
```

for Python processes launched directly on the host when they should use the Docker database.

If a separate local PostgreSQL service is used instead, configure the host/port accordingly.

---

# Start the Stack

Foreground:

```bash
docker compose up --build
```

Detached:

```bash
docker compose up --build -d
```

Status:

```bash
docker compose ps
```

Useful URLs:

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/assets
http://127.0.0.1:8000/measurements
http://127.0.0.1:8000/kpis/measurements
```

---

# Database Initialization

Compose mounts:

```text
sql/schema.sql    → /docker-entrypoint-initdb.d/01-schema.sql
sql/seed_data.sql → /docker-entrypoint-initdb.d/02-seed.sql
```

A fresh volume creates:

```text
regions
asset_types
assets
simulation_runs
measurements
storage_specs
```

and loads development seed data.

Initialization scripts run only when the PostgreSQL data directory is empty.

---

# Rebuild after Schema Changes

Keep existing volume:

```bash
docker compose down
docker compose up --build -d
```

This rebuilds the image but does **not** re-run database initialization scripts.

Recreate database and seed:

```bash
docker compose down -v
docker compose up --build -d
```

> `docker compose down -v` permanently deletes the Compose development database volume.

Use it deliberately after schema/seed changes and for release-candidate clean rebuilds.

`v0.11.1` removes the former `measurements.interval_minutes` and `measurements.energy_kwh` columns, so moving a local `v0.11.0` development volume to this version requires this clean rebuild while the project still uses SQL initialization instead of migrations.

---

# Health Check and Startup Order

PostgreSQL health check:

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
  interval: 5s
  timeout: 5s
  retries: 5
  start_period: 10s
```

API dependency:

```yaml
depends_on:
  db:
    condition: service_healthy
```

This prevents FastAPI from starting before PostgreSQL reports readiness.

---

# Port Model

| Component | Container port | Host port | Purpose |
|---|---:|---:|---|
| FastAPI | `8000` | `8000` | HTTP / Swagger |
| PostgreSQL | `5432` | `5433` | Optional host DB access |

---

# Logs and Troubleshooting

All logs:

```bash
docker compose logs
```

Specific services:

```bash
docker compose logs api
docker compose logs db
```

Follow API logs:

```bash
docker compose logs -f api
```

Inspect resolved Compose configuration:

```bash
docker compose config
```

Open PostgreSQL shell:

```bash
docker compose exec db psql -U postgres -d energy_operations
```

Useful database checks after a simulation demo:

```sql
SELECT *
FROM simulation_runs
ORDER BY simulation_run_id DESC
LIMIT 5;
```

```sql
SELECT
    simulation_run_id,
    COUNT(*) AS measurement_count,
    MIN(measurement_time) AS first_measurement,
    MAX(measurement_time) AS last_measurement
FROM measurements
WHERE simulation_run_id IS NOT NULL
GROUP BY simulation_run_id
ORDER BY simulation_run_id DESC;
```

---

# Automated Tests

The pytest suite uses the dedicated test database name:

```text
energy_operations_test
```

Run:

```bash
py -m pytest -v
```

Key release paths:

```bash
py -m pytest -m integration -v
py -m pytest -m smoke -v
py -m pytest -m failure -v
py -m ruff check src tests scripts
```

The current setup does not run pytest inside Compose. The test process is launched from the host and must be able to connect to the configured test database.

---

# Manual Simulation Demo

Developer demo:

```bash
py -m scripts.run_simulation_demo
```

The script:

- creates a current-hour historical simulation window,
- executes the real `execute_simulation_run()` service,
- writes a `simulation_runs` row,
- persists generated point-in-time measurements,
- derives intervals in memory,
- prints persisted counts and interval counts per asset,
- returns a non-zero process exit code if its checks fail.

Important:

> The demo writes to the regular application database configured by `.env`.

Because `measurements` has a unique `(asset_id, measurement_time)` constraint, repeating an identical generated timestamp window can fail with a duplicate conflict. Use the demo intentionally against a development database.

---

# Current Docker / Deployment Limitations

- No production image hardening.
- No non-root container user.
- No separate development and production Compose files.
- No FastAPI container health check.
- No automated database migration framework.
- No Dockerized test runner.
- No CI image build/test pipeline yet.
- No cloud deployment or managed PostgreSQL configuration yet.
- No public simulation REST endpoint yet.

---

# Next Deployment Steps

1. Keep the current API + PostgreSQL Compose stack stable through the Energy Balance and frontend-ready backend blocks.
2. Add the React/TypeScript frontend to the local Full-Stack start for the `v1.0.0` portfolio MVP.
3. Add a portfolio architecture diagram, screenshots and a clear release/demo workflow.
4. Introduce a migration strategy when preserving real environments/data across schema versions becomes necessary.
5. Add CI, production hardening and cloud-oriented configuration after the first Full-Stack MVP unless a concrete deployment need appears earlier.

