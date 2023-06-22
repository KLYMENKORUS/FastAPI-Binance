from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (create_async_engine, async_sessionmaker,
                                    AsyncSession, AsyncAttrs)
from sqlalchemy.orm import DeclarativeBase
from src.config import DATABASE_URL


class Base(AsyncAttrs, DeclarativeBase):
    ...


# create async engine
engine = create_async_engine(DATABASE_URL, future=True, echo=True)

# create session
async_session_maker = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
