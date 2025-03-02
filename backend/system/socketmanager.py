"""
    All keys need to be set two times -> actual key and shadow key
"""
import urllib.parse
import socketio, urllib,json
from datetime import datetime
import asyncio
sio = socketio.AsyncServer(async_mode='asgi',cors_allowed_origins="*")
socket_app = socketio.ASGIApp(sio)

FORMAT = "%Y-%m-%d %H:%M:%S"
FIVE_MINUTES = 5*60

async def send_periodic_messages(sid):
    while True:
        await asyncio.sleep(1)
        await sio.emit("message", "hello world", to=sid)

def get_query_args(query_string):
    return urllib.parse.parse_qs(query_string)

async def broadcast_user_online(name):
    # broadcasting to all the clients including the joined client itself
    # as the user will show himself as online also
    print("sending online")
    await sio.emit("online",name)

@sio.event
async def connect(sid,environ,*args):
    scope = environ.get("asgi.scope")
    # check auth here as well
    # maybe we can also do this the user should first hit the http /
    # the / controller set the user to the cache
    # then we check the cache here and if not found in the cache then dont' allow the user
    # here just set him online
    app = scope.get("app")
    query_string = scope.get("query_string").decode()
    query = get_query_args(query_string)
    name = query.get("name")[0]
    cache = app.state.cache.client
    timestamp = datetime.now().strftime(FORMAT)
    await cache.hset(name,mapping={"timestamp": timestamp, "status": "online"})
    await cache.hset(f"shadowkey:{name}",mapping={"timestamp": timestamp, "status": "online"})
    await cache.expire(f"shadowkey:{name}",FIVE_MINUTES)
    # TODO: check auth
    # update the cache
    print("connected",sid,name)
    # await sio.emit("message","hello world")
    # asyncio.create_task(send_periodic_messages(sid))
    sio.start_background_task(broadcast_user_online,name)

@sio.event
async def disconnect(sid):
    # TODO: check auth
    # update the cache
    print("disconnected",sid)

@sio.event
async def heartbeat(sid,environ,*args):
    environ = sio.get_environ(sid)
    scope = environ.get("asgi.scope")
    app = scope.get("app")
    query_string = scope.get("query_string").decode()
    query = get_query_args(query_string)
    name = query.get("name")[0]
    cache = app.state.cache.client
    timestamp = datetime.now().strftime(FORMAT)
    await cache.hset(name,mapping={"timestamp": timestamp, "status": "online"})
    await cache.hset(f"shadowkey:{name}",mapping={"timestamp": timestamp, "status": "online"})
    await cache.expire(f"shadowkey:{name}",FIVE_MINUTES)