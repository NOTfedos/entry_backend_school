from pydantic import BaseSettings

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker


class DBSettings(BaseSettings):
    """ Parses variables from environment on instantiation """

    database_uri: str  # could break up into scheme, username, password, host, db


engine = create_async_engine(DBSettings().database_uri, echo=True)
Base = declarative_base()
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
