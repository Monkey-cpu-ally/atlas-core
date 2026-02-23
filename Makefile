.PHONY: help backend-dev backend-install backend-import-check

help:
	@echo "Targets:"
	@echo "  backend-install      Install backend dependencies into .venv"
	@echo "  backend-import-check Verify backend imports (no server)"
	@echo "  backend-dev          Run FastAPI backend (reload)"

backend-install:
	@if [ ! -d .venv ]; then python3 -m venv .venv; fi
	@. .venv/bin/activate && python -m pip install -U pip && python -m pip install -e .

backend-import-check: backend-install
	@. .venv/bin/activate && python -c "from atlas_core_new.main import app; print('OK', app.title, app.version, 'routes', len(app.routes))"

backend-dev: backend-install
	@. .venv/bin/activate && python -m uvicorn atlas_core_new.main:app --reload --host 127.0.0.1 --port 8000

