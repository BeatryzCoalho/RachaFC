from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTStrategy, AuthenticationBackend, CookieTransport
from fastapi_users.db import BeanieUserDatabase
from app.models import User, UserCreate, UserUpdate
import os

SECRET = os.getenv("JWT_SECRET", "trocar-essa-chave")

async def get_user_db():
    yield BeanieUserDatabase(User)

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=60*60*12)


cookie_transport = CookieTransport(cookie_name="acess_token", cookie_max_age=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy= get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, str](
    get_user_db,
    [auth_backend],
)

auth_router = fastapi_users.get_auth_router(auth_backend)
register_router = fastapi_users.get_register_router(User, UserCreate)
users_router = fastapi_users.get_register_router(User, UserUpdate)

current_user = fastapi_users.current_user(active=True)
current_staff =  fastapi_users.current_staff(active=True, optional=False)