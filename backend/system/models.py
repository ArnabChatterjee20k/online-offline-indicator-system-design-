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
    with session:
        user = User(name=name,last_seen=last_seen,color="red")
        await session.add(user)
        await session.commit()
        return user