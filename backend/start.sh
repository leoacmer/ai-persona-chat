#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "=== 1. Python ==="
python --version

echo "=== 2. Config ==="
python -c "
import config
print('DATABASE_URL:', config.DATABASE_URL, flush=True)
print('AI_BASE:', config.AI_API_BASE, flush=True)
print('AI_MODEL:', config.AI_MODEL, flush=True)
"

echo "=== 3. Import test ==="
python -c "from app import app; print('Import OK', flush=True)"

echo "=== 4. Wait for DB ready ==="
for i in 1 2 3 4 5 6; do
  echo "Attempt $i/6 ..."
  python -c "
from db import _get_engine, Base
import asyncio, sqlalchemy
from sqlalchemy import text

async def test():
    engine = _get_engine()
    async with engine.connect() as conn:
        await conn.execute(text('SELECT 1'))
    print('DB connection OK', flush=True)
asyncio.run(test())
" && break
  echo "Retrying in 5s..."
  sleep 5
done

echo "=== 5. Init DB ==="
python -c "
from db import init_db
import asyncio
asyncio.run(init_db())
print('Init OK', flush=True)
"

echo "=== 6. Seed personas ==="
python -c "
from db import _get_sessionmaker
from services.persona_service import seed_default_personas
import asyncio

async def seed():
    async with _get_sessionmaker()() as db:
        await seed_default_personas(db)
    print('Seed OK', flush=True)
asyncio.run(seed())
"

echo "=== 7. Starting uvicorn ==="
exec python -m uvicorn app:app --host 0.0.0.0 --port $PORT
