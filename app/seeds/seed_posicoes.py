import asyncio, os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models import Posicao

load_dotenv()

SYSTEM_RULES = [
    {"posicao": "Goleiro", "is_system": True},
    {"posicao": "Zagueiro", "is_system": True},
    {"posicao": "Fixo", "is_system": True},
    {"posicao": "Meia", "is_system": True},
    {"posicao": "Ala", "is_system": True},
    {"posicao": "Atacante", "is_system": True},
       
]

async def ensure_system_position():
    client = AsyncIOMotorClient(os.getenv("MONGO_URL"))
    db = client.get_default_database()

    await init_beanie(database=db, document_models=[Posicao])

    for posi in SYSTEM_RULES:
        existe = await Posicao.find_one(Posicao.posicao == posi["posicao"])
        if existe:
            existe.is_system = True
            await existe.save()
            posicoes = posi["posicao"]
            print(f"Posição {posicoes} já existia, só atualizada.")
        else:
            posicoes = posi["posicao"]
            await Posicao(
                posicao=posi["posicao"],
                is_system=True            
                ).insert()
            print(f"+ Criada posição do sistema: {posicoes}")
    
    print("Seed de posições concluído.")

if __name__ == "__ensure_system_position__":
    asyncio.run(ensure_system_position())