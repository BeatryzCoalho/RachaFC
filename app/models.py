from beanie import Document, Link, Indexed, before_event
from typing import Optional, Literal
from datetime import date, datetime
from pydantic import Field
from fastapi_users_db_beanie import BeanieBaseUser
from fastapi_users import schemas


##USER (login/autentificação)
class User(BeanieBaseUser, Document):
    is_admin: bool = False

    class Settings(BeanieBaseUser.Settings):
        name = "users"

# Esquemas para criação/atualização
class UserCreate(schemas.BaseUserCreate):
    is_admin: Optional[bool] = False

class UserUpdate(schemas.BaseUserUpdate):
    is_admin: Optional[bool] = None


##TABELA DE POSICOES
class Posicao(Document):
    posicao: Indexed(str, unique=True)
    is_system: bool = False 

    class Settings: name = 'posicoes'
    
    async def delete(self, *args, **kwargs):
        if self.is_system:
            raise ValueError("Posições do sistema não podem ser apagadas.")
        return await super().delete(*args, **kwargs)

##TABELA DE DADOS DO JOGADOR
class Jogador(Document):
    nome: str
    apelido: Optional[str] = None
    posicao: Optional[Link[Posicao]] = None
    foto_url: Optional[str] = None
    ativo: bool = True
    user: Optional[Link[User]] = None
    class Settings: name = 'jogadores'


##TABELA DE TEMPORADAS
class Temporada(Document):
    nome: str
    inicio: date
    fim: date
    class Settings: name = 'temporadas'

##TABELA DE PARTIDAS
class Partida(Document):
    temporada: Link[Temporada]
    semana_inicio: date
    semana_fim: date
    numero: int
    class Settings:
        name = "partidas"

    



##TABELA DE REGRAS
class Regra(Document):
    nome: Indexed(str, unique=True)
    apelido: str = Field(..., descrition="Nome amigável, ex: Cartão vermelho")
    ponto: float = 0.0   
    is_system: bool = False 

    class Settings: name = 'regras'

    async def delete(self, *args, **kwargs):
        if self.is_system:
            raise ValueError("Regras do sistema não podem ser apagadas.")
        return await super().delete(*args, **kwargs)


##TABELA DE RANKING
class Evento(Document):
    partida: Link[Partida]
    jogador: Link[Jogador]
    tipo: Link[Regra]
    criado_em: datetime = Field(default_factory=datetime.utcnow)
    class Settings: name ='eventos'




