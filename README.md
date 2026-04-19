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

## Regenerating the TypeScript API client

The frontend types in `apps/web/src/lib/api/generated.ts` are generated from the live FastAPI OpenAPI schema. Whenever backend schemas change, regenerate:

```bash
# Terminal 1
make api-dev

# Terminal 2
cd apps/web && npm run api:types
```

`apps/web/src/lib/api/types.ts` re-exports friendly aliases over the generated `components["schemas"]` shapes. `queries.ts` and `mutations.ts` expose TanStack Query hooks keyed by `queryKeys` for invalidation hygiene.

## Training blocks and progression

A training block spans N weeks with fixed workouts on fixed days. The user picks each exercise's week-1 weight and may attach a `fixed_increment` progression rule (e.g., `+2.5 kg / week`). On block create/update, the server calls `propagate_block_progressions`, which:

- Groups rows across weeks by `(day_index, order_index, exercise_id)`.
- Uses the lowest-week row with a rule as the anchor (its `target_weight` is the base).
- Fills later weeks as `base + (week_index - anchor_week) * weight_increment`.
- Skips rows flagged `manual_override = true` so hand-edited cells survive re-propagation.
- Stores provenance in `progression_snapshot_json` (`{source, anchor_week, base_weight, increment, computed_week}`).

The block editor can also trigger propagation explicitly via `POST /blocks/{block_id}/propagate-progressions`. When planned workouts are generated from a block, target weights and snapshots are copied verbatim — materialization never recomputes.

## Verification

- Backend tests:

  ```bash
  .venv/bin/pytest apps/api/tests -q
  ```

- Frontend typecheck and production build:

  ```bash
  cd apps/web && npm run typecheck && npm run build
  ```

## Production

- Render builds from the repo root `Dockerfile`.
- The frontend is compiled during the Docker build and copied into `apps/api/app/static`.
- FastAPI serves the SPA in production and exposes API routes under `/api`.
- Configure `DATABASE_URL` with the Neon connection string and set `SECRET_KEY`, `ADMIN_USERNAME`, and `ADMIN_PASSWORD`.
