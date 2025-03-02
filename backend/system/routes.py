from fastapi import APIRouter,Query,Request
from pydantic import BaseModel
from .db import DBSession
from .cache import get_cache
from datetime import datetime
from .models import save_user,update_user,get_users
import asyncio
class UserList(BaseModel):
    id:int
    name:str
    last_seen:str
    color:str

class Details(BaseModel):
    name:str

FORMAT = "%Y-%m-%d %H:%M:%S"
FIVE_MINUTES = 5*60

# dummy auth api route
# rest of the interaction with the sockets
router = APIRouter()
@router.get("/users")
async def users(request:Request,session:DBSession,data:Details=Query(...)):
    async with session:
        cache = get_cache(request=request).client
        users = await get_users(session,data.name)
        timestamp = datetime.now().strftime(FORMAT)
        if not await cache.hget(data.name,"timestamp"):
            await save_user(session=session,name=data.name,last_seen=timestamp)
        res = []
        # FIXME: instead of querying all users from db
        # we can search in the cache as well
        # by having a separate namespace for a separate room
        for user in users:
            if await cache.hget(user.name,"timestamp") or user.name == data.name:
                user.last_seen = "online"
            res.append(user)
        return res