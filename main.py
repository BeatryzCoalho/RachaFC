import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from dotenv import load_dotenv

from app.models import( Posicao, Jogador, Temporada, Partida, Regra, Evento)
from app.seeds.seed_regras import ensure_system_rules
from app.seeds.seed_posicoes import ensure_system_position
from app.routers.router_jogadores import router as rota_jogadores
from app.routers.router_partida import router as rota_partida
from app.auth import auth_router, register_router, users_router
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
        document_models=[User, Posicao, Jogador, Temporada, Partida, Regra, Evento],
    )


    await ensure_system_rules()
    await ensure_system_position()

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(register_router, prefix="/auth", tags=["auth"])
app.include_router(users_router, prefix="/auth", tags=["auth"])
app.include_router(rota_jogadores, prefix="/jogadores", tags=["jogadores"])
app.include_router(rota_partida, prefix="/partida", tags=["partida"])

@app.get("/health")
async def health():
    return {"ok": True}