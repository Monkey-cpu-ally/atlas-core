#!/usr/bin/env bash
set -euo pipefail

# Local dev helper for Atlas Core backend (FastAPI).
#
# Usage:
#   bash scripts/dev_backend.sh
#
# Notes:
# - Uses a local venv at ./.venv
# - Optional features may require extra env vars (OPENAI_API_KEY, DATABASE_URL, etc.)

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${VENV_DIR:-.venv}"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "Python not found: ${PYTHON_BIN}"
  exit 1
fi

if [[ ! -d "${VENV_DIR}" ]]; then
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

python -m pip install -U pip
python -m pip install -e .

exec python -m uvicorn atlas_core_new.main:app --reload --host "${HOST}" --port "${PORT}"

