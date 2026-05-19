#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "=== Starting AI Persona Chat ==="
python --version

echo "=== Import test ==="
python -c "from app import app; print('Import OK', flush=True)"

echo "=== Starting uvicorn ==="
exec python -m uvicorn app:app --host 0.0.0.0 --port $PORT
