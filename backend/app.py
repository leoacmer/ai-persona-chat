import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from services.persona_service import seed_default_personas
from routes import chat, upload


@asynccontextmanager
async def lifespan(app: FastAPI):
    await seed_default_personas()
    yield


app = FastAPI(title="AI Persona Chat", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(upload.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
