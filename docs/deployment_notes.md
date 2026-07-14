# Deployment Notes

## Purpose

This document describes the local containerized environment of the Energy Operations Platform.

The Docker foundation was established in `v0.9.x`; `v0.10.0` verifies that the expanded five-table energy-domain schema initializes and runs in the same reproducible environment.

Related documentation:

- [`database_notes.md`](database_notes.md)
- [`api_reference.md`](api_reference.md)
- [`test_strategy.md`](test_strategy.md)

## Current Status

The local stack consists of:

```text
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
- persistent database files through `db_data`,
- host API access on port `8000`,
- optional host database access on port `5433`.

## Services

### `api`

The API service:

- builds from the local `Dockerfile`,
- exposes `8000:8000`,
- reads `.env`,
- overrides `DB_HOST` with `db`,
- depends on a healthy PostgreSQL service,
- starts Uvicorn on `0.0.0.0:8000`.

### `db`

The database service:

- uses `postgres:18`,
- reads `POSTGRES_USER`, `POSTGRES_PASSWORD` and `POSTGRES_DB`,
- exposes host port `5433` to container port `5432`,
- stores data in the named volume `db_data`,
- initializes `schema.sql` and `seed_data.sql` for a new volume,
- reports readiness through `pg_isready`.

## Dockerfile

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

## Ignored Files

`.dockerignore` excludes local or private content from the image build context, including:

```text
.git
.env
.venv/
venv/
__pycache__/
.pytest_cache/
logs/
*.log
*.zip
private_learning_notes.md
```

The real `.env` file must never be committed or copied into the image.

## Environment Variables

Create `.env` from `.env.example`:

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

Compose changes only the API database hostname:

```yaml
environment:
  DB_HOST: db
```

Inside the Compose network:

```text
host: db
port: 5432
```

From Windows or another host process:

```text
host: localhost
port: 5433
```

## Start the Stack

Foreground mode:

```bash
docker compose up --build
```

Detached mode:

```bash
docker compose up --build -d
```

Check status:

```bash
docker compose ps
```

Useful URLs:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/assets
http://127.0.0.1:8000/measurements
http://127.0.0.1:8000/kpis/measurements
```

## Database Initialization

Compose mounts:

```text
sql/schema.sql    → /docker-entrypoint-initdb.d/01-schema.sql
sql/seed_data.sql → /docker-entrypoint-initdb.d/02-seed.sql
```

For a new volume, PostgreSQL creates:

```text
regions
asset_types
assets
measurements
storage_specs
```

and loads the development dataset.

Initialization scripts run only when the PostgreSQL data directory is empty.

## Rebuild after Schema Changes

Keeping the volume:

```bash
docker compose down
docker compose up --build -d
```

This rebuilds images but does not re-run the SQL initialization scripts.

Recreating the database:

```bash
docker compose down -v
docker compose up --build -d
```

> `docker compose down -v` permanently deletes the Compose development database volume.

Use it deliberately when the schema or initial seed data changes.

## Health Check and Startup Order

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

This prevents the API from attempting its first database connection while PostgreSQL is still starting.

## Port Model

| Component | Container port | Host port | Purpose |
|---|---:|---:|---|
| FastAPI | `8000` | `8000` | HTTP and Swagger access |
| PostgreSQL | `5432` | `5433` | Optional host database access |

## Logs and Troubleshooting

Show all logs:

```bash
docker compose logs
```

Service-specific logs:

```bash
docker compose logs api
docker compose logs db
```

Follow API logs:

```bash
docker compose logs -f api
```

Resolve and inspect the final Compose configuration:

```bash
docker compose config
```

Common checks:

```bash
docker compose ps
docker compose exec db psql -U postgres -d energy_operations
docker compose logs db
docker compose logs api
```

## Stop and Restart

Stop containers and keep data:

```bash
docker compose down
```

Restart:

```bash
docker compose up --build -d
```

## Automated Tests

The current pytest suite runs against the dedicated local test database rather than the development database container by default:

```bash
py -m pytest -v
```

Running tests in Docker or CI is not yet part of the current setup.

## Current Limitations

- No production image hardening.
- No non-root container user.
- No separate development and production Compose files.
- No API health check inside Compose.
- No automated database migrations.
- No Dockerized test runner.
- No cloud deployment or managed database configuration.

## Next Deployment Steps

1. Keep the current local stack stable during simulation development.
2. Introduce database migrations before Azure deployment.
3. Add CI tests and image build validation.
4. Add an architecture diagram for the portfolio MVP.
5. Add production-oriented configuration only when the backend domain logic is mature.
