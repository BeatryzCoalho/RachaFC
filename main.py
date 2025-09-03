import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from dotenv import load_dotenv

from app.models import( Posicao, Jogador, Temporada, Partida, Regra, Evento)
from app.seeds.seed_regras import ensure_system_rules
from app.seeds.seed_posicoes import ensure_system_position
load_dotenv()
MONGO_URL = os.getenv("MONGO_URL", "")

app= FastAPI(title="Racha FC API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")

async def on_startup():
    if not MONGO_URL:
        raise RuntimeError("MONGO_URL não definido no .env")
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.get_default_database()

    await init_beanie(
        database=db,
        document_models=[Posicao, Jogador, Temporada, Partida, Regra, Evento],
    )


    await ensure_system_rules()
    await ensure_system_position()

@app.get("/health")
async def health():
    return {"ok": True}