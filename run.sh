#!/usr/bin/env bash
set -euo pipefail

(
  cd frontend
  npm run build
)

source .venv/bin/activate
uv run main.py
