API_DIR=apps/api
WEB_DIR=apps/web

.PHONY: db-up db-down api-install api-dev web-install web-dev migrate seed test

db-up:
	docker compose up -d postgres

db-down:
	docker compose down

api-install:
	cd $(API_DIR) && python3 -m pip install -e .[dev]

api-dev:
	cd $(API_DIR) && uvicorn app.main:app --reload --port 8000

web-install:
	cd $(WEB_DIR) && npm install

web-dev:
	cd $(WEB_DIR) && npm run dev -- --host

migrate:
	cd $(API_DIR) && alembic upgrade head

seed:
	cd $(API_DIR) && python3 -m app.bootstrap

test:
	cd $(API_DIR) && pytest -q
