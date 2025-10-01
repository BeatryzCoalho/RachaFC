from fastapi import APIRouter, HTTPException, Depends
from typing import List
from pydantic import BaseModel
from beanie import PydanticObjectId
from app.models import Evento, Partida, Jogador, Regra
from app.auth import current_staff, current_user

router = APIRouter()

class EventoIn(BaseModel):
    partida_id: str
    jogador_id: str
    regra_id: str

class EventoOut(BaseModel):
    id:str
    partida_id:str
    jogador_id:str
    regra_id:str
    criado_em: str

def serialize_evento(evento: Evento) -> EventoOut:
    return EventoOut(
        id=str(evento.id),
        partida_id=str(evento.partida_id),
        jogador_id=str(evento.jogador.id),
        regra_id=str(evento.tipo.id),
        criado_em=str(evento.criado_em),
    )

@router.get("/", response_model=List[EventoOut])
async def listar_eventos(user=Depends(current_staff)):
    eventos = await Evento.find_all(fetch_links=True).to_list()
    return [serialize_evento(evento) for evento in eventos]


@router.post("/", response_model=EventoOut)
async def criar_evento(payload: EventoIn, user=Depends(current_staff)):
    partida = await Partida.get(PydanticObjectId(payload.partida_id))
    if not partida:
        raise HTTPException(404, "Partida não encontrada")

    jogador = await Jogador.get(PydanticObjectId(payload.jogador_id))
    if not jogador:
        raise HTTPException(404, "Jogador não encontrado")

    regra = await Regra.get(PydanticObjectId(payload.regra_id))
    if not regra:
        raise HTTPException(404, "Regra não encontrada")

    evento = Evento(partida=partida, jogador=jogador, tipo=regra)
    await evento.insert()
    evento =  await get(evento.id, fetch_links=True)

    return serialize_evento(evento)

@router.post("/partida/{partida_id}/campeao_semana")
async def definir_campeoes_semana(partida_id:str, campeoes:List[str]):
    """
    campeoes = lista de IDs de jogadores que venceram na semana.
    Para os outros jogadores da partida, aplica PERDEDOR_SEMANA.
    """

    partida = await Partida.get(PydanticObjectId(partida_id))
    if not partida:
        raise HTTPException(404, "Partida não encontrada")

    regra_campeao = await Regra.find_one(Regra.nome == "CAMPEAO_SEMANA")
    regra_perdedor = await Regra.find_one(Regra.nome == "PERDEDOR_SEMANA")

    if not regra_campeao or not regra_perdedor:
        raise HTTPException(500, "Regras não configuradas")

    for jogador_id in campeoes:
        jogador = await Jogador.get(PydanticObjectId(jogador_id))
        if jogador:
            evento= Evento(partida=partida, jogador=jogador, tipo=regra_campeao)
            await evento.insert()

    for jogador in jogadores_partida:
        if str(jogador.id) not in campeoes:
            evento = Evento(partida=partida, jogador=jogador, tipo=regra_perdedor)
            await evento.insert()

    return {"ok":True, "campeoes":campeoes}

@router.put("/{evento_id}", response_model=EventoOut)
async def atualizar_evento(evento_id: str, payload:EventoIn, user=Depends(current_staff)):
    evento = await Evento.get(PydanticObjectId(evento_id), fetch_links=True)
    if not evento:
        raise HTTPException(404, "Evento não encontrado")

    partida = await Partida.get(PydanticObjectId(payload.partida_id))
    if not partida:
        raise HTTPException(404, "Partida não encontrada")

    jogador = await Jogador.get(PydanticObjectId(payload.jogador_id))
    if not jogador:
        raise HTTPException(404, "Jogador não encontrado")

    regra = await Regra.get(PydanticObjectId(payload.regra_id))
    if not regra:
        raise HTTPException(404, "Regra não encontrada")

    evento.partida = partida
    evento.jogador = jogador
    evento.tipo = regra

    await evento.save()
    evento = await Evento.get(evento.id, fetch_links=True)

    return serialize_evento(evento)


@router.delete("/{evento_id}")
async def deletar_evento(evento_id:str, user=Depends(current_staff)):
    evento = await Evento.get(PydanticObjectId(evento_id))
    if not evento:
        raise HTTPException(404, "Evento não encontrado")
    await evento.delete()
    return {"message": "Evento deletado com sucesso"}
