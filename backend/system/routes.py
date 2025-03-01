from fastapi import APIRouter,Query,Request
from pydantic import BaseModel
from .db import DBSession
from .cache import get_cache
from datetime import datetime
class UserList(BaseModel):
    id:int
    name:str
    last_seen:str
    color:str

class Details(BaseModel):
    name:str

FORMAT = "%Y-%m-%d %H:%M:%S"

router = APIRouter()
@router.get("/")
async def get_users(request:Request,db:DBSession,data:Details=Query(...)):
    cache = get_cache(request=request).client
    await cache.hset(data.name,mapping={
        "status":"online",
        "timestamp":datetime.now().strftime(FORMAT)
    })
    return datetime.now().strftime(FORMAT)