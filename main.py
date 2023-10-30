from fastapi import FastAPI
from auth_routes import auth_router
from database import engine
from models import Base
from orders_routers import orders_router
from fastapi_jwt_auth.auth_jwt import AuthJWT
from schemas import Settings

app = FastAPI()


@AuthJWT.load_config
def get_config():
    return Settings()


app.include_router(auth_router)
app.include_router(orders_router)


# @app.get("/")
# async def root():
#     return {"message": "Hello World"}
#
#
# @app.get("/hello/{name}")
# async def say_hello(name: str):
#     return {"message": f"Hello {name}"}
