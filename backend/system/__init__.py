from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from system.socketmanager import socket_app , broadcast_user_offline
from system.db import test_db, sessionmanager
from system.models import update_user
from system.cache import Cache
from system.redis_pubsub import PubSub
from contextlib import asynccontextmanager
async def callback(name,timestamp):
    async with sessionmanager.session() as session:
        await update_user(session=session,last_seen=timestamp,name=name)
        await broadcast_user_offline(name,timestamp)

@asynccontextmanager
async def startup_event(app):
    app.state.cache = Cache()
    pubsub = PubSub()
    await pubsub.setup_keyspace_notification(callback)
    await test_db()
    yield
    await pubsub.close()
    await app.state.cache.close()

def create_api():
    api = FastAPI(lifespan=startup_event)
    from .routes import router
    api.include_router(router)
    api.mount("/",socket_app)
    api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Should be a list, not a string
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

    
    return api
