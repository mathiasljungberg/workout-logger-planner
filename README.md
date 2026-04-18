# workout-logger-planner

Personal training tracker for planning workouts, authoring progression-focused training blocks, logging sessions, and reviewing adherence and volume.

## Stack

- Backend: FastAPI, SQLAlchemy 2.x, Alembic
- Frontend: React + Vite + TypeScript
- Local database: PostgreSQL via Docker Compose
- Production hosting: Render web service + Neon Postgres

## Repo layout

- `apps/api`: backend app, models, routes, migrations, tests
- `apps/web`: React frontend
- `infra/render.yaml`: Render deployment config
- `docker-compose.yml`: local PostgreSQL
- `tasks/todo.md`: implementation ledger

## Local development

1. Create a root `.env` from `.env.example`.
2. Start Postgres:

   ```bash
   make db-up
   ```

3. Create the Python environment and install backend deps:

   ```bash
   UV_CACHE_DIR=/tmp/uv-cache uv venv .venv
   UV_CACHE_DIR=/tmp/uv-cache uv pip install --python .venv/bin/python -e ./apps/api[dev]
   ```

4. Install frontend deps:

   ```bash
   cd apps/web && npm install
   ```

5. Run migrations and seed the default admin user plus starter exercises:

   ```bash
   make migrate
   make seed
   ```

6. Start the apps in separate terminals:

   ```bash
   make api-dev
   make web-dev
   ```

Default seeded credentials come from `.env` and default to `admin` / `admin`.

In local frontend development, requests to `/api` are proxied by Vite to `http://localhost:8000`, so login works even if `VITE_API_BASE_URL` is unset in the web process. Use `VITE_API_BASE_URL` only when you need the frontend to call a different backend origin explicitly.
When the frontend calls the backend directly across ports, FastAPI allows the dev origin configured by `CORS_ORIGINS`, which defaults to `http://localhost:5173`.

## Verification

- Backend tests:

  ```bash
  .venv/bin/pytest apps/api/tests -q
  ```

- Frontend production build:

  ```bash
  cd apps/web && npm run build
  ```

## Production

- Render builds from the repo root `Dockerfile`.
- The frontend is compiled during the Docker build and copied into `apps/api/app/static`.
- FastAPI serves the SPA in production and exposes API routes under `/api`.
- Configure `DATABASE_URL` with the Neon connection string and set `SECRET_KEY`, `ADMIN_USERNAME`, and `ADMIN_PASSWORD`.
