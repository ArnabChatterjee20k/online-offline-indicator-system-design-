from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession,async_sessionmaker,create_async_engine, AsyncConnection
import contextlib,os
from typing import AsyncIterator
class Base(DeclarativeBase):
    pass

class DBSessionManager:
    def __init__(self,url):
        self.engine = create_async_engine(url)
        self.sessionmaker = async_sessionmaker(bind=self.engine,autocommit=False)

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self.sessionmaker is None:
            raise Exception("No session found")
        session = self.sessionmaker()
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.rollback()

# database_url = os.environ.get("ASYNC_DB_URL")
database_url = "sqlite+aiosqlite:///database_name.db"
sessionmanager = DBSessionManager(database_url)

async def get_db_session():
    async with sessionmanager.session() as session:
        yield session

async def test_db():
    async with sessionmanager.session() as session:
        if isinstance(session, AsyncSession):
            print("db is working")
    async with sessionmanager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

from fastapi import Depends
from typing import Annotated

DBSession = Annotated[AsyncSession,Depends(get_db_session)]