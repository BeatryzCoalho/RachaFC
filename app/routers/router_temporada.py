from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
from beanie import PydanticObjectId
from app.models import Temporada
from datetime import timedelta, date
from fastapi import Depends
from app.auth import current_staff
router = APIRouter()

class TemporadaIn(BaseModel):
    nome:str
    inicio:str
    fim: str

class TemporadaOut(BaseModel):
    id: str
    nome: str
    inicio: str
    fim: str

async def gerar_partidas(temporada: Temporada):
    inicio = temporada.inicio
    fim = temporada.fim

    numero = 1 
    data_atual = inicio

    while data_atual <= fim:
        semana_inicio = data_atual
        semana_fim = min(data_atual + timedelta(days=6), fim)

    partida = Partida(
        temporada=temporada,
        numero=numero,
        semana_inicio=semana_inicio,
        semana_fim=semana_fim,
    )

    await partida.insert()
    print(f"Patida criada para {inicio}")
    numero += 1
    data_atual += timedelta(weeks=1)

def serializer_temporada(temporada: Temporada) -> TemporadaOut:
    return TemporadaOut(
        id=str(temporada.id),
        nome=temporada.nome,
        inicio=str(temporada.inicio),
        fim=str(temporada.fim)
    )


@router.get("/", response_model=List[TemporadaOut])
async def listar_temporadas():
    docs =  await Temporada.find_all().to_list()
    return [serializer_temporada(temporada) for temporada in docs]


@router.post("/", response_model=TemporadaOut)
async def criar_temporada(payload:TemporadaIn, user=Depends(current_staff)):

    temporada = Temporada(nome=payload.nome, inicio=payload.inicio, fim=payload.fim)
    await temporada.insert()
    await gerar_partidas(temporada)
    return serializer_temporada(temporada)


@router.put("/{temp_id}", response_model=TemporadaOut)
async def atualizarTemporada(temp_id:str, payload: TemporadaIn):
    temporada = await Temporada.get(PydanticObjectId(temp_id))
    if not temporada:
        raise HTTPException(404, "Temporada não encontrada")
    temporada.nome, temporada.inicio, temporada.fim = payload.nome, payload.inicio, payload.fim
    await tempora.save()
    return serializer_temporada(temporada)


@router.delete("/{temp_id}")
async def deletar(temp_id: str):
    temporada = await Temporada.get(PydanticObjectId(temp_id))
    if not temporada:
        raise HTTPException(404, "Temporada não encontrada")
    await temporada.delete()
    return {"ok": True}