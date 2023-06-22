import asyncio
import pytest
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine,\
    async_sessionmaker, AsyncSession
from src.config import DATABASE_URL_TEST
from database import metadata, get_async_session
from main import app

# create async test engine
test_engine = create_async_engine(
    DATABASE_URL_TEST, future=True, echo=True, poolclass=NullPool
)

# create test session
test_async_session = async_sessionmaker(
    test_engine, expire_on_commit=False, class_=AsyncSession
)

metadata.bind = test_engine


async def get_async_test_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_async_session() as session:
        yield session

app.dependency_overrides[get_async_session] = get_async_test_session


@pytest.fixture(scope='session', autouse=True)
async def prepare_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)


# SETUP
@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create a new FastAPI TestClient instance"""
    async with AsyncClient(app=app, base_url='http://tets') as async_client:
        yield async_client


@pytest.fixture(scope='session', autouse=True)
async def async_session_test():
    """Test async session"""
    engine = create_async_engine(
        DATABASE_URL_TEST, future=True, echo=True, poolclass=NullPool
    )
    async_session_maker = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession)
    yield async_session_maker



