import asyncio, os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models import Regra

load_dotenv()

SYSTEM_RULES = [
    {"nome": "GOL", "apelido": "Gol", "ponto": 0},
    {"nome": "AMARELO", "apelido": "Cartão amarelo", "ponto": 0},
    {"nome": "VERMELHO", "apelido": "Cartão vermelho", "ponto": 0},
    {"nome": "CAMPEAO_SEMANA", "apelido": "Campeão da semana", "ponto": 0},
    {"nome": "PERDEDOR_SEMANA", "apelido": "Perdedor da semana", "ponto": 0},
]

async def ensure_system_rules():
    client = AsyncIOMotorClient(os.getenv("MONGO_URL"))
    db = client.get_default_database()

    await init_beanie(database=db, document_models=[Regra])

    for regra in SYSTEM_RULES:
        existe = await Regra.find_one(Regra.nome == regra["nome"])
        if existe:
            existe.is_system = True
            existe.apelido = regra["apelido"]
            await existe.save()
            nome = regra["nome"]
            print(f"Regra {nome} já existia, só atualizada.")
        else:
            nome = regra["nome"]
            await Regra(
                nome=regra["nome"],
                apelido=regra["apelido"],
                ponto=regra["ponto"],
                is_system=True            
                ).insert()
            print(f"+ Criada regra do sistema: {nome}")
    
    print("Seed de regras concluído.")

if __name__ == "__ensure_system_rules__":
    asyncio.run(ensure_system_rules())