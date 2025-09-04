from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from beanie import PydanticObjectId
from app.models import Partida, Temporada

router = APIRouter()

class PartidaIn(BaseModel):
    temporada_id: str
    data: str
    
class PartidaOut(BaseModel):
    id: str
    temporada_id: str
    data:str


def serialize_partida(partida: Partida) -> PartidaOut:
    return PartidaOut(
        id=str(partida.id),
        temporada_id=str(partida.temporada.id)
        data=str(partida.data)
    )

## esse @router é um decorador de rota, ele diz qual operação minha função abaixo representará
@route.get("/", response_model=List[PartidaOut])
async def listar_partidas():
    partidas = await Partida.find_all(fecth_links=True).to_list()
    return [serialize_partida(partida) for partida in partidas]

@route.post("/", response_model=PartidaOut)
async def criar_partida(payload: PartidaIn):
    temporada =  await Temporada.get(PydanticObjectId(payload.temporada_id))
    if not temporada:
        raise HTTPException(404, "Temporada não encontrada")
    partida = Partida(
        temporada=temporada,
        data=payload.data
    )
    await partida.insert()
    partida = await Partida.get(partida.id, fecth_links=True)
    return serialize_partida(partida)

@router.put("/{partida_id}", response_model=PartidaOut)
async def atualizar_partida(partida_id: str, payload:PartidaIn):
    partida = await Partida.get(PydanticObjectId(partida_id))
    if not partida:
        raise HTTPException(404, "Partida não encontrada")
    temporada = await Temporada.get(PydanticObjectId(payload.temporada_id))
    if not temporada:
        raise HTTPException(404, "Temporada não encontrada")

    partida.temporada = temporada
    partida.data = payload.data

    await partida.save()
    partida = await Partida.get(partida.id, fecth_links=True)
    return serialize_partida(partida)

@router.delete("/{partida_id}")
async def deletar(partida_id: str):
    partida = await Partida.get(PydanticObjectId(partida_id))
    if not partida:
        raise HTTPException(404, "Partida não encontrada")
    await partida.delete()
    return {"ok": True}
