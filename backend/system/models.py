from sqlalchemy.orm import mapped_column,MappedColumn
from .db import Base
class User(Base):
    __tablename__ = 'users'
    id:MappedColumn[int] = mapped_column("id",primary_key=True,autoincrement=True)
    name:MappedColumn[str] = mapped_column("name")
    last_seen:MappedColumn[str] = mapped_column("last_seen")
    color:MappedColumn[str] = mapped_column("color")

from sqlalchemy.ext.asyncio import AsyncSession
async def save_user(session:AsyncSession,name,last_seen):
    query = select(User).filter(User.name==name)
    user = (await session.execute(query)).scalar()
    if user:
        return user
    user = User(name=name,last_seen=last_seen,color="")
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

async def get_users(session:AsyncSession,name:str):
    query = select(User)
    return (await session.execute(query)).scalars().all()

from sqlalchemy import select
async def update_user(session:AsyncSession,name,last_seen):
    query = select(User).filter(User.name == name)
    user = (await session.execute(query)).scalar()
    if not user:
        return
    user.last_seen = last_seen
    await session.commit()