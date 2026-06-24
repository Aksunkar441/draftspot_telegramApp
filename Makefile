.PHONY: backend frontend build seed-help

backend:
	cd backend && SERVERLESS=true ../.venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

frontend:
	cd frontend && npm run dev -- --host 127.0.0.1 --port 5173

build:
	cd frontend && npm run build
	cd backend && ../.venv/bin/python -m compileall app

seed-help:
	@echo "Run backend/sql/dev_seed.sql manually in the Supabase dev SQL Editor."
	@echo "Never run dev_seed.sql against production."
