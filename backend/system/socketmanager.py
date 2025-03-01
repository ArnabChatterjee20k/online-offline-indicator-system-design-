import socketio
sio = socketio.AsyncServer(async_mode='asgi',cors_allowed_origins="*")
socket_app = socketio.ASGIApp(sio)

@sio.event
async def connect(sid,*args):
    print(args)
    # TODO: check auth
    # update the cache
    print("connected",sid)
    await sio.emit("message","hello world")

@sio.event
async def disconnect(sid):
    # TODO: check auth
    # update the cache
    print("disconnected",sid)