from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import async_session, engine
from .init_db import init_database
from .routes.media import router as media_routes
from .routes.tweets import router as tweets_routes
from .routes.users import router as users_routes

app = FastAPI()

API_PREFIX = "/api"

app.include_router(users_routes, prefix=API_PREFIX)
app.include_router(tweets_routes, prefix=API_PREFIX)
app.include_router(media_routes, prefix=API_PREFIX)

ORIGINS = [
    "http://localhost",
    "http://localhost:80",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    # Инициализация должна выполняться 1 раз в 1 потоке
    session = async_session()
    await init_database(engine=engine, session=session)
