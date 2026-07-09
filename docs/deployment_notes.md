# Deployment Notes

This document tracks deployment-related work for the Energy Operations Platform.

For endpoint behavior, see [`api_reference.md`](api_reference.md).  
For database details, see [`database_notes.md`](database_notes.md).  
For tests and test data handling, see [`test_strategy.md`](test_strategy.md).

## Current Deployment Status

Docker support started in `v0.9.0`.

The current setup provides:

- an initial `Dockerfile` for the FastAPI application,
- a `.dockerignore` file to keep the Docker build context clean,
- a Docker image build command,
- a Docker run command with port mapping,
- a first container-based check through `/health` and `/docs`.

PostgreSQL is not yet containerized. The current Docker step focuses on the API container first.

## Dockerfile

The current `Dockerfile` builds the FastAPI application image.

Main steps:

1. Use a Python base image.
2. Set `/app` as the working directory.
3. Copy `requirements.txt`.
4. Install Python dependencies.
5. Copy the project files.
6. Expose port `8000`.
7. Start the API with Uvicorn.

Current application start command:

```bash
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

The `--host 0.0.0.0` setting is important because the API must listen inside the container in a way that can be reached through Docker port mapping.

## Docker Ignore File

The `.dockerignore` file excludes local and private files from the Docker build context.

Current excluded categories include:

- Git metadata,
- Python cache files,
- pytest cache,
- local virtual environments,
- `.env`,
- logs,
- private learning notes,
- zip archives.

This keeps the image smaller and avoids copying local/private files into the Docker build context.

## Build the API Image

From the project root:

```bash
docker build -t energy-operations-api:v0.9.0 .
```

Expected result:

- Docker builds an image named `energy-operations-api`.
- The tag `v0.9.0` marks the current Docker milestone.

Check available images:

```bash
docker images
```

## Run the API Container

Run the API container locally:

```bash
docker run --name energy-api-test -p 8000:8000 energy-operations-api:v0.9.0
```

Open:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
```

Useful container commands:

```bash
docker ps
docker ps -a
docker logs energy-api-test
docker stop energy-api-test
docker rm energy-api-test
```

## Current Database Limitation

At `v0.9.0`, only the FastAPI app is containerized.

The PostgreSQL database still runs outside Docker. This means:

- `/health` and `/docs` can work without database access,
- database-backed endpoints such as `/stations` need a reachable PostgreSQL connection,
- `localhost` inside a container refers to the container itself, not necessarily the host machine.

If PostgreSQL runs on the host machine, a Docker-specific host value may be needed, for example:

```env
DB_HOST=host.docker.internal
```

This is a local development workaround. The cleaner long-term setup is Docker Compose with separate `api` and `db` services on the same Docker network.

## Environment Variables

The project uses environment variables for database configuration.

Current example:

```env
DB_NAME=energy_operations
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=5432
```

For local Docker runs, these values may need to be passed through Docker using an environment file or explicit `-e` parameters.

Example pattern:

```bash
docker run --env-file .env -p 8000:8000 energy-operations-api:v0.9.0
```

Do not copy real `.env` files into the image. `.env` is intentionally excluded by `.dockerignore`.

## What v0.9.0 Does Not Solve Yet

The current Docker milestone does not yet include:

- Docker Compose,
- PostgreSQL container setup,
- automatic database initialization,
- automatic seed data loading,
- production-ready Docker image hardening,
- cloud deployment,
- CI/CD.

These are intentionally left for later steps.

## Next Deployment Steps

Recommended next steps:

1. Add `docker-compose.yml` with separate `api` and `db` services.
2. Move database host configuration toward service names, for example `DB_HOST=db`.
3. Add PostgreSQL environment variables to Compose.
4. Decide how schema and seed data should be loaded in the containerized setup.
5. Update setup documentation after Compose works reliably.
6. Later: prepare a simple architecture diagram showing API, DB and local development flow.

## Summary

`v0.9.0` is the first deployment-readiness step.

The project can now define and build a FastAPI Docker image. The next major improvement is to run the API and PostgreSQL together through Docker Compose so the local setup becomes more reproducible.
