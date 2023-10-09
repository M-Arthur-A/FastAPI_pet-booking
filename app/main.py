import time

from fastapi import FastAPI, Query, Depends, Request
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqladmin import Admin
from typing import Optional
from datetime import date
from pydantic import BaseModel
from dataclasses import dataclass
from contextlib import asynccontextmanager
from redis import asyncio as aioredis
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings
from app.database import engine
from app.users.router import router as router_users
from app.bookings.router import router as router_bookings
from app.hotels.router import router as router_hotels
from app.hotels.rooms.router import router as router_rooms
from app.images.router import router as router_images
from app.importer.router import router as router_importer
from app.admin.views import UsersAdmin, BookingsAdmin, HotelsAdmin, RoomsAdmin
from app.admin.auth import authentication_backend
from app.logger import logger


@asynccontextmanager # запуск кода при запуске и выходе приложения (настройка кэша)
async def lifespan(app: FastAPI):
    # при входе (до yield)
    redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}")
    FastAPICache.init(RedisBackend(redis), prefix="cache")
    yield
    # при выходе (после yield)


app =  FastAPI(lifespan=lifespan) #, docs_url=None, redoc_url=None)

app.include_router(router_users)
app.include_router(router_bookings)
app.include_router(router_hotels)
app.include_router(router_rooms)
app.include_router(router_images)
app.include_router(router_importer)


instrumentator = Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=[".*admin.*", "/metrics"],
)
Instrumentator().instrument(app).expose(app)


admin = Admin(app, engine, authentication_backend=authentication_backend)

admin.add_view(UsersAdmin)
admin.add_view(BookingsAdmin)
admin.add_view(HotelsAdmin)
admin.add_view(RoomsAdmin)

app.mount("/static", StaticFiles(directory="app/static"), "static")

origins = [
    "http://localhost:3000", # 3000 - порт, на котором работает фронтенд на React.js
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers",
                   "Access-Control-Allow-Origin", "Authorization"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    # При подключении Prometheus + Grafana подобный лог не требуется
    # logger.info(
    #     "Request handling time",
    #     extra={
    #         "process_time": round(process_time, 4),
    #     },
    # )
    return response



class SHotel(BaseModel): # S - scheme
    address: str
    name: str
    start: int

    class Config: # для работы с ответом Алхимии нам необходимо обращаться к атрибутам через точку
        from_attributes = True
        # orm_mode = True # в старых версиях

@dataclass
class GetHotelsArgs:
    loc: str
    date_from: date
    date_to: date
    has_spa: bool | None = None
    stars: Optional[int] = Query(None, ge=1, le=5)



@app.get("/hotels") # , response_model=list[SHotel]
def get_hotels(search_args: GetHotelsArgs = Depends()
        # loc: str,
        # date_from: date,
        # date_to: date,
        # has_spa: bool | None = None,
        # stars: Optional[int] = Query(None, ge=1, le=5),
        ):
    hotels = [
        {
            "address": "Lenin street",
            "name": "Super hotel",
            "start": 5,
        }
    ]
    return hotels
