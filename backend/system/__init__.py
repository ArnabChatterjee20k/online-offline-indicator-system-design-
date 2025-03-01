from fastapi import FastAPI
from system.socketmanager import socket_app
from system.db import test_db
from system.cache import Cache
from contextlib import asynccontextmanager

@asynccontextmanager
async def startup_event(app):
    app.state.cache = Cache()
    await test_db()
    yield
    await app.state.cache.close()

def create_api():
    api = FastAPI(lifespan=startup_event)
    from .routes import router
    api.include_router(router)
    api.mount("/",socket_app)

    return api
