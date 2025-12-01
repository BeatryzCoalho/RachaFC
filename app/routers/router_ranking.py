from fastapi import APIRouter, HTTPException
from beanie import PydanticObjectId
from typing import List
from app.models import Temporada, Partida, Evento, Jogador, Regra
from bson import ObjectId, DBRef
router = APIRouter()
from pydantic.json import pydantic_encoder
import json

@router.get("/temporada/{temporada_id}")
async def ranking_temporada(temporada_id: str):

    try:
        temporada = await Temporada.get(ObjectId(temporada_id))
    except Exception:
        raise HTTPException(400, "ID de temporada inválido")
   
    if not temporada:
        raise HTTPException(404, "Temporada não encontrada")

    partidas = await Partida.find(
        Partida.temporada.id == temporada.id
    ).to_list()

    if not partidas:
        raise HTTPException(404, "Nenhuma partida encontrada para essa temporada")

    partidas_ids = [ObjectId(str(p.id)) for p in partidas]

    eventos = await Evento.find({
        "partida.$id": {"$in": partidas_ids}
    }).to_list()
    
    if not eventos:
        raise HTTPException(404, "Nenhum evento encontrado para essa temporada")

    ranking = {}
    for e in eventos:
        await e.fetch_link(Evento.partida)
        await e.fetch_link(Evento.jogador)
        await e.fetch_link(Evento.tipo)
    for evento in eventos:
        jogador = evento.jogador
        regra = await Regra.get(evento.tipo.id) if isinstance(evento.tipo, Regra) else None
      
        if jogador.id not in ranking:
            ranking[jogador.id] = {
                "joagador": jogador.nome,
                "apelido": jogador.apelido,
                "posicao": jogador.posicao.posicao if jogador.posicao else None,
                "total_pontos": 0,
                "gols_total": 0,
                "cartoes_amarelos": 0,
                "cartoes_vermelhos": 0,
                "dados_temporada": []
            }

        pontos = regra.ponto if regra else 0
        ranking[jogador.id]['total_pontos'] += pontos

        if regra and regra.nome == "GOL":
            ranking[jogador.id]["gols_total"] += 1
        if regra and regra.nome == "VERMELHO":
            ranking[jogador.id]["cartoes_amarelos"] += 1
        if regra and regra.nome == "AMARELO":
            ranking[jogador.id]["cartoes_vermelhos"] += 1

        ranking[jogador.id]["dados_temporada"].append({
            "data_evento": evento.criado_em.strftime("%d-%m-%Y"),
            "ponto": pontos,
            "regra": regra.apelido if regra else "desconhecida"
        })

    return sorted(ranking.values(), key=lambda x: x["total_pontos"], reverse=True)
@router.get("/partida/{partida_id}")
async def ranking_partida(partida_id:str):
    partida = await Partida.get(PydanticObjectId(partida_id))
    if not partida:
        raise HTTPException(404, "Partida não encontrada")

    eventos = await Evento.find(Evento.partida.id == partida.id, fetch_links=True).to_list()

    ranking={}

    for evento in eventos:
        jogador = evento.jogador
        regra = await Regra.get(evento.tipo.id) if isinstance(evento.tipo, Regra) else None

        if jogador.id not in ranking:
            ranking[jogador.id] = {
                "jogador": jogador.nome,
                "apelido": jogador.apelido,
                "pontos_partida":0
            }

        pontos = regra.ponto if regra else 0
        ranking[jogador.id]["pontos_partida"] += pontos

    ranking_ordenado = sorted(ranking.values(), key=lambda x: x["pontos_partida"], reverse=True)

    return ranking_ordenado