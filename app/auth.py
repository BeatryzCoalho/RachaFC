import os
from typing import Optional
from fastapi import Depends, HTTPException, status, Request, Response
from fastapi_users import FastAPIUsers, BaseUserManager
from fastapi_users.authentication import CookieTransport, AuthenticationBackend, JWTStrategy
from fastapi_users_db_beanie import BeanieUserDatabase
from bson import ObjectId

from app.models import User, UserCreate, UserUpdate

SECRET = os.getenv("JWT_SECRET", "trocar-essa-chave")

cookie_transport = CookieTransport(cookie_name="access_token", cookie_max_age=3600)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=60 * 60 * 12)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)



async def get_user_db():
    yield BeanieUserDatabase(User)



class UserManager(BaseUserManager[User, str]):
    user_db_model = User

    async def on_after_register(self, user: User, request: Request | None = None)-> None:
        print(f"Usuário registrado: {user.email}")

    async def on_after_login( self, user: User, request: Request | None = None, response: Response | None = None)-> None:
        print(f"Usuário fez login: {user.email}")

    async def on_after_forgot_password(self, user:User, token:str, request: Request | None = None) -> None:
            print(f"Reset de senha para {user.email}, token={token}")

    async def on_after_request_verify(self, user:User, token:str, request: Request | None = None)-> None:
        print(f"Verificação solicitada para {user.email}, token={token}")

    def parse_id(self, user_id)-> str:
        if isinstance(user_id, ObjectId):
            return str(user_id)
        return user_id
    
    def generate_id(self) ->str:
        return str(ObjectId())

async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)



fastapi_users = FastAPIUsers[User, str](
    get_user_manager,
    [auth_backend],
)

auth_router = fastapi_users.get_auth_router(auth_backend)
register_router = fastapi_users.get_register_router(User, UserCreate)
users_router = fastapi_users.get_users_router(User, UserUpdate)


current_user = fastapi_users.current_user(active=True)

async def current_staff(user: User = Depends(current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem acessar essa rota"
        )
    return user  



