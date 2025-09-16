from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel, Field
from beanie import PydanticObjectId
from app.models import Jogador, Posicao

router = APIRouter()


class JogadorIn(BaseModel):
    nome:str
    apelido: Optional[str] = None
    posicao_id: Optional[str] = Field(default=None, des ="ID da posição")
    user_id: Optional[str] = None

class JogadorUpdateSelf(BaseModel):
    apelido: Optional[str] = None
    foto_url: Optional[str] = None


class JogadorUpdateAdmin(BaseModel):
    apelido: Optional[str] = None
    foto_url: Optional[str] = None
    ativo: Optional[str] = None
    posicao_id:Optional[str] = None


class JogadorOut(BaseModel):
    id: str
    nome: str
    apelido: Optional[str] 
    foto_url: Optional[str] 
    ativo: bool
    posicao: Optional[str]


async def serializer_get_posicao(posicao_id: Optional[str]) -> Optional[Posicao]:
    if not posicao_id:
        return None
    try:
        ## oid significa ObjectId que é um identificador do Mongo 
        oid = PydanticObjectId(posicao_id) 
    except Exception:
        raise HTTPException(400, "posicao_id inválido")

    posicao = await Posicao.get(oid)

    if not posicao:
        raise HTTPException(404, "Posição não encontrada")
    
    return posicao

def serialize_jogador(jogador: Jogador) -> JogadorOut:
    return JogadorOut(
        id=str(jogador.id),
        nome=jogador.nome,
        apelido=jogador.apelido,
        foto_url=jogador.foto_url,
        posicao=(jogador.posicao.posicao if jogador.posicao else None),
        ativo=jogador.ativo,    
    )

@router.get("/", response_model=List[JogadorOut])
async def listar_jogadores(user=Depends(current_staff)):
    ## o fecth_links ele serve pra avisar que o find_all tem que trazer os id, mais o que esta vinculado nele
    lista_jogadores = await Jogador.find_all(fecth_links=True).to_list()
    return [serialize_jogador(jogador) for jogador in lista_jogadores]


@router.get("/ativos", response_model=List[JogadorOut])
async def listar_jogadores_ativos(user=Depends(current_user)):
   
    lista_jogadores = await Jogador.find(Jogador.ativo == True, fecth_links=True).to_list()
    return [serialize_jogador(jogador) for jogador in lista_jogadores]


@router.get("/", response_model=JogadorOut)
async def get_jogador(jogador_id: str):
    try:
        oid = PydanticObjectId(jogador_id)
    except Exception:
        raise HTTPException(400, "ID inválido")

    jogador = await Jogador.get(oid, fetch_links=True)
    if not jogador:
        raise HTTPException(404, "Jogador não encontrado")
    return serialize_jogador(jogador)

@router.post("/", response_model=JogadorOut)
async def criar_jogador(payload: JogadorIn, user=Depends(current_staff)):
    posicao = None
    if payload.posicao_id:
        posicao = await serializer_get_posicao(payload.posicao_id)
        if not posicao:
            raise HTTPException(404, "Posição não encontrada")
    
    jogador = Jogador(nome=payload.nome, apelido=payload.apelido, posicao=posicao, ativo=True)
    await jogador.insert()
    jogador = await Jogador.get(jogador.id, fetch_links=True)
    return serialize_jogador(jogador)


@router.put("/{jogador_id}", response_model=JogadorOut)
async def atualizar_jogador_admin(jogador_id:str, payload: JogadorIn, user=Depends(current_staff)):
    try:
        oid = PydanticObjectId(jogador_id)
    except Exception:
        raise HTTPException(400, "ID inválida")

    jogador = await Jogador.get(oid, fetch_links=True)

    if not jogador:
        raise HTTPException(404, "Jogador não encontrado")

    posicao = await serializer_get_posicao(payload.posicao_id)
    if payload.foto_url is not None:
        jogador.foto_url = payload.foto_url
     if payload.apelido is not None:
        jogador.apelido = payload.apelido
     if payload.posicao is not None:
        jogador.posicao_id = posicao
     if payload.ativo is not None:
        jogador.ativo = payload.ativo

    await jogador.save()
    jogador = await Jogador.get(jogador.id, fecth_links=True)
    return serialize_jogador()


@router.put("/me", response_model=JogadorOut)
async def atualizar_meu_perfil(payload: JogadorUpdateSelf, user=Depends(current_user)):
    jogador = await Jogador.find_one(Jogador.user.id == user.id, fetch_links=True)
    if not jogador:
        raise HTTPException(404, "Jogador não encontrado")

    if payload.apelido is not None:
        jogador.apelido = payload.apelido
    if payload.foto_url is not None:
        jogador.foto_url = payload.foto_url

    await jogador.save()
    return serialize_jogador(jogador)

@router.delete("/{jogador_id}")
async def deletar_jogador(jogador_id: str, user=Depends(current_staff)):
    try: 
        oid = PydanticObjectId(jogador_id)
    except Exception:
        raise HTTPException(400, "ID inválido")

    jogador = await Jogador.get(oid)
    if not jogador:
        raise HTTPException(404, "Jogador não encontrado")
    await jogador.delete()
    return {"message": f"jogador {jogador.nome} removido com sucesso"}