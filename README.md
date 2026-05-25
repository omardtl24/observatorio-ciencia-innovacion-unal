# Observatorio de Gestión y Análisis de Indicadores para la Ciencia y la Innovación

Official website for the Observatorio de Gestión y Análisis de Indicadores para la Ciencia y la Innovación, Faculty of Sciences, Universidad Nacional de Colombia. The platform combines a public web interface, an API, a PostgreSQL database, and analytic components to visualize and manage indicators related to science, technology, and innovation.

## Project Overview

The repository is organized as a multi-service application:

- `backend/`: Python API service built with Flask and run with Gunicorn in production.
- `frontend/`: React application built with Vite.
- `db/`: PostgreSQL schema and seed resources for local database setups.
- `shiny/`: R/Shiny analytics applications and server setup.
- `nginx/`: HTTPS reverse proxy that routes traffic to the app services.
- `shared_files/`: shared storage used by backend and Shiny services in production.

## Environment Files with `gen_envs.py`

The `gen_envs.py` script manages environment files across the repository.

It supports two modes:

- `build`: scans the repository for `.env`, `.env.dev`, and `.env.prod` files, stores the collected structure as plain JSON, and encrypts it into `config.gpg`.
- `decrypt`: decrypts `config.gpg` and recreates the matching `.env` files in their original folders.

Typical usage from the repository root:

```bash
python gen_envs.py build --root . --output config.gpg
python gen_envs.py decrypt --root . --output config.gpg
```

Useful options:

- `--force-scan` with `build` ignores an existing `config.json` and rescans the filesystem.
- `--force` with `decrypt` overwrites existing env files without prompting.
- `--dry-run` with `decrypt` previews the files that would be written.

The script requires `gpg` to be installed and available in `PATH`.

## Run in Development

Development uses [docker-compose.dev.yml](docker-compose.dev.yml). It mounts the source code, runs the frontend with Vite dev server, starts the backend in debug mode, and exposes Adminer for database inspection.

```bash
docker compose -f docker-compose.dev.yml up --build
```

Main services in dev:

- PostgreSQL database on the private Docker network.
- Backend API on port `5000`.
- Frontend dev server on port `5173`.
- Shiny server for interactive analytics.
- Nginx reverse proxy exposing the application over `80` and `443`.
- Adminer on port `8080` for database access.

## Run in Production

Production uses [docker-compose.prod.yml](docker-compose.prod.yml). It builds the application images, runs the backend with Gunicorn, serves the frontend in preview mode after building it, and routes external traffic through Nginx. The production stack does not start a database container; the backend connects to an external PostgreSQL instance instead.

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Main differences in prod:

- Backend runs with Gunicorn instead of the Flask debug server.
- Frontend is built before being served.
- Shared resources are mounted from `shared_files/`.
- Database credentials are provided for an external PostgreSQL server, not a container in the compose stack.
- No Adminer service is included.

Before starting production, make sure the backend env configuration points `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, and `DB_PASSWORD` to the external database.

## Quick Summary of Components

- Backend: API and business logic.
- Frontend: user-facing web interface.
- Database: PostgreSQL persistence layer.
- Shiny: data analysis and visualization apps.
- Nginx: HTTPS entrypoint and request router.
- Shared files: common storage for generated or uploaded assets.
