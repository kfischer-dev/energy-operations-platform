# Deployment Notes

This document tracks deployment-related work for the Energy Operations Platform.

For endpoint behavior, see [`api_reference.md`](api_reference.md).  
For database details, see [`database_notes.md`](database_notes.md).  
For tests and test data handling, see [`test_strategy.md`](test_strategy.md).

## Current Deployment Status

As of `v0.9.2`, the complete local application stack can be started reliably with Docker Compose.

The current setup provides:

- a FastAPI image built from the project `Dockerfile`,
- a PostgreSQL 18 container,
- an internal Compose network for API-to-database communication,
- automatic schema and development seed initialization for a new database volume,
- persistent PostgreSQL storage through a named volume,
- host access to FastAPI on port `8000`,
- host access to the containerized database on port `5433`.

## Services

### `api`

The API service:

- is built from the local `Dockerfile`,
- exposes container port `8000` on host port `8000`,
- reads the project `.env` file,
- overrides `DB_HOST` with `db`,
- waits until the PostgreSQL service reports a healthy state before starting.

Within the Compose network, `db` is the hostname of the PostgreSQL service.

### `db`

The database service:

- uses the `postgres:18` image,
- reads `POSTGRES_USER`, `POSTGRES_PASSWORD` and `POSTGRES_DB`,
- exposes container port `5432` on host port `5433`,
- stores database files in the named volume `db_data`,
- initializes schema and development seed data when the volume is created for the first time,
- uses `pg_isready` as a health check so Compose can verify database readiness.

## Dockerfile

The current `Dockerfile`:

1. Uses `python:3.14-slim`.
2. Sets `/app` as the working directory.
3. Copies and installs `requirements.txt` separately for better Docker layer caching.
4. Copies the project files.
5. Exposes port `8000`.
6. Starts Uvicorn on all container interfaces.

Start command:

```bash
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

`--host 0.0.0.0` is required so the API can be reached through Docker port mapping.

## Environment Variables

Create `.env` from `.env.example`.

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

The FastAPI and PostgreSQL credentials must match while both services use the same database user.

For the API service, Compose overrides:

```yaml
DB_HOST: db
```

`DB_PORT` remains `5432` inside the Compose network. Host port `5433` is only used when accessing the PostgreSQL container from Windows or another host process.

Real `.env` files must not be committed or copied into the image.

## Start the Full Stack

From the project root:

```bash
docker compose up --build
```

Run in detached mode:

```bash
docker compose up --build -d
```

Check service status:

```bash
docker compose ps
```

Useful endpoints:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/assets
http://127.0.0.1:8000/kpis/measurements
```

## Logs and Troubleshooting

Show all Compose logs:

```bash
docker compose logs
```

Show logs for one service:

```bash
docker compose logs api
docker compose logs db
```

Follow logs continuously:

```bash
docker compose logs -f api
```

Show the resolved Compose configuration:

```bash
docker compose config
```

This is useful for checking resolved environment variables, ports, volumes and service configuration.

## Stop and Restart

Stop and remove the containers while keeping the database volume:

```bash
docker compose down
```

Restart the stack:

```bash
docker compose up --build
```

## Database Initialization and Volumes

The following files are mounted into PostgreSQL's initialization directory:

```text
sql/schema.sql    -> /docker-entrypoint-initdb.d/01-schema.sql
sql/seed_data.sql -> /docker-entrypoint-initdb.d/02-seed.sql
```

PostgreSQL runs these scripts only when the database data directory is initialized for the first time.

Changing `schema.sql` or `seed_data.sql` does not automatically rerun them for an existing `db_data` volume.

To delete the development database volume and initialize it again:

```bash
docker compose down -v
docker compose up --build
```

> Warning: `docker compose down -v` deletes the persistent database data of this Compose project.

## Port Model

| Component | Container port | Host port | Purpose |
|---|---:|---:|---|
| FastAPI | `8000` | `8000` | Browser/API access from the host |
| PostgreSQL | `5432` | `5433` | Optional database access from the host |

Inside Compose, the API connects to:

```text
host: db
port: 5432
```

The host mapping `5433:5432` does not change the internal database port.

## Database Readiness

The PostgreSQL service uses a health check based on `pg_isready`.

The API service depends on:

```yaml
depends_on:
  db:
    condition: service_healthy
```

This ensures that the API starts only after PostgreSQL is ready to accept connections, rather than merely after the database container process has started.

## Tests

The existing pytest suite continues to run against the dedicated local test database unless explicitly reconfigured.

```bash
py -m pytest -v
```

Running the test suite inside Docker is not part of the current `v0.9.x` scope.

## Next Deployment Steps

Recommended next steps:

1. Keep the Compose setup stable while the energy-domain model grows.
2. Update schema initialization when new domain tables are added.
3. Add an architecture diagram before the portfolio MVP.
4. Consider Azure deployment only after the backend domain logic provides visible value.

## Summary

`v0.9.2` completes the current Docker foundation with a reproducible and readiness-aware local development environment.

FastAPI and PostgreSQL run as separate services, communicate through the Compose network, initialize the current schema and demo data from the repository, and coordinate startup through a database health check. This completes the main Docker Compose foundation and enables the project to move toward the richer energy-domain and simulation features.
