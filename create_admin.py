import asyncio 
import os 
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from fastapi_users.password import PasswordHelper

from app.models import User, Posicao, Jogador, Temporada, Partida, Regra, Evento
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "")
if not MONGO_URL:
    raise RuntimeError("MONGO_URL não definido no .env")

async def create_admin():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.get_default_database()

    await init_beanie(
        database=db,
        document_models=[User, Posicao, Jogador, Temporada, Partida, Regra, Evento],
    )

    existing = await User.find_one(User.email == "admin@racha.com")
    if existing:
        print("Usuário admin já existe>", existing.email)
        return
    
    pwd_helper = PasswordHelper()
    hashed_password = pwd_helper.hash("minhasenha123")

    user = User(
        email="admin@racha.com",
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=False,
        is_verficied=True,
        is_admin=True,
    )

    await user.insert()
    print("Usuário admin criado com sucesso:", user.email)

if __name__ == "__main__":
    asyncio.run(create_admin())