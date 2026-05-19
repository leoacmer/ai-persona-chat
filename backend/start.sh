#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "=== 1. Python ==="
python --version

echo "=== 2. Basic imports ==="
python -c "
import sys; print('sys OK', flush=True)
import fastapi; print('fastapi OK', flush=True)
import sqlalchemy; print('sqlalchemy OK', flush=True)
import openai; print('openai OK', flush=True)
import uvicorn; print('uvicorn OK', flush=True)
import aiosqlite; print('aiosqlite OK', flush=True)
import asyncpg; print('asyncpg OK', flush=True)
"

echo "=== 3. Config ==="
python -c "
import config
print('DATABASE_URL:', config.DATABASE_URL[:30], flush=True)
print('AI_BASE:', config.AI_API_BASE, flush=True)
print('AI_MODEL:', config.AI_MODEL, flush=True)
"

echo "=== 4. DB engine ==="
python -c "
from db import _get_engine, Base
engine = _get_engine()
print('Engine OK', flush=True)
"

echo "=== 5. Models ==="
python -c "
from models import Persona, Conversation, Message, Memory
print('Models OK', flush=True)
"

echo "=== 6. Services ==="
python -c "
from services.ai_service import chat_completion
print('ai_service OK', flush=True)
from services.persona_service import get_persona
print('persona_service OK', flush=True)
"

echo "=== 7. App ==="
python -c "
from app import app
print('App OK', flush=True)
"

echo "=== 8. Starting ==="
exec python -m uvicorn app:app --host 0.0.0.0 --port $PORT
