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


def _to_out_(p: Partida) -> PartidaOut:
    return PartidaOut(
        id=str(p.id),
        temporada_id=str(p.temporada.id)
        data=str(p.data)
    )

## esse @router é um decorador de rota, ele diz qual operação minha função abaixo representará
@route.get("/", response_model=List[PartidaOut])
async def listar_partidas():
    docs = await Partida.find_all(fecth_links=True).to_list()
    return [_to_out(p) for p in docs]

@route.post("/", response_model=PartidaOut)
async def criar_partida(payload: PartidaIn):
    temp =  await Temporada.get(PydanticObjectId(payload.temporada_id))
    if not temp:
        raise HTTPException(404, "Temporada não encontrada")
    p = Partida(
        temporada=temp,
        data=payload.data
    )
    await p.insert()
    p = await Partida.get(p.id, fecth_links=True)
    return _to_out(p)

@router.put("/{partida_id}", response_model=PartidaOut)
async def atualizar_partida(partida_id: str, payload:PartidaIn):
    p = await Partida.get(PydanticObjectId(partida_id))
    if not p:
        raise HTTPException(404, "Partida não encontrada")
    temp = await Temporada.get(PydanticObjectId(payload.temporada_id))
    if not temp:
        raise HTTPException(404, "Temporada não encontrada")

    p.temporada = temp
    p.data = payload.data

    await p.save()
    p = await Partida.get(p.id, fecth_links=True)
    return _to_out(p)

@router.delete("/{partida_id}")
async def deletar(partida_id: str):
    p = await Partida.get(PydanticObjectId(partida_id))
    if not p:
        raise HTTPException(404, "Partida não encontrada")
    await p.delete()
    return {"ok": True}
