#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "=== 1. Python version ==="
python --version

echo "=== 2. Import test ==="
python -c "
import sys, traceback
try:
    from app import app
    print('Import OK', flush=True)
except Exception:
    traceback.print_exc()
    sys.exit(1)
"

echo "=== 3. Starting uvicorn ==="
exec python -m uvicorn app:app --host 0.0.0.0 --port $PORT
