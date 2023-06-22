from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.database import Base
from sqlalchemy import Column, String, Integer, Select, \
    select, Result, MetaData, Table, desc
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.orm import Mapped, mapped_column


metadata = MetaData()

binance_data = Table(
    'binance_data',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('interval', String(10), nullable=False),
    Column('symbol', String(128), nullable=False),
    Column('open_time', String(128), nullable=False),
    Column('open', String(255), nullable=False),
    Column('high', String(255), nullable=False),
    Column('low', String(255), nullable=False),
    Column('close', String(255), nullable=False),
    Column('volume', String(255), nullable=False)
)


class BinanceData(Base):
    """
    Models Binance Data:
    Attributes:
        - id: The id of the symbol
        - interval: The interval between
        - symbol: The symbol
        - open_time: The open time of the symbol
        - open: amount at the opening of the transaction
        - high: maximum amount
        - low: minimum amount
        - close: amount at the close of the transaction
        - volume: volume
        - close_time: the close time of the transaction
    """

    __tablename__ = 'binance_data'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    interval: Mapped[str] = mapped_column(
        String(10), nullable=False
    )
    symbol: Mapped[str] = mapped_column(
        String(128), nullable=False
    )
    open_time: Mapped[str] = mapped_column(
        String(128), nullable=False
    )
    open: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    high: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    low: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    close: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    volume: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    @staticmethod
    async def create_binance_data(session: AsyncSession, kwargs: dict[str, Any]):
        """Create a row binance data in the database"""
        new_row = BinanceData(**kwargs)
        session.add(new_row)
        try:
            await session.commit()
            return new_row

        except Exception:
            await session.rollback()
            raise

    @staticmethod
    async def get_all_data_by_symbol(symbol: str, session: AsyncSession):
        """Returns all data for a symbol in the database"""
        query: Select = select(BinanceData).filter_by(symbol=symbol)
        query_result: Result = await session.execute(query)
        return query_result.scalars().all()


csv_data = Table(
    'csv_data',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('filename', String(128), nullable=False),
    Column('data', BYTEA, nullable=False)
)


class CSVData(Base):
    """
    Model for CSV data:
    Attributes:
        - filename: filename (string)
        - data: data (bytes)
    """

    __tablename__ = 'csv_data'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    filename: Mapped[str] = mapped_column(
        String(128), nullable=False
    )
    data = mapped_column(
        BYTEA, nullable=False
    )

    @staticmethod
    async def create_csv_data(session: AsyncSession, filename: str, data: bytes):
        """Create a CSV data in database"""
        new_csv_data = CSVData(filename=filename, data=data)
        session.add(new_csv_data)
        try:
            await session.commit()
            return new_csv_data
        except Exception:
            await session.rollback()
            raise

    @staticmethod
    async def get_last_csv_data(session: AsyncSession):
        """Returns the last record csv data"""
        query: Select = select(CSVData)
        query: Select = query.order_by(desc(CSVData.id)).limit(1)
        query_result: Result = await session.execute(query)
        return query_result.fetchone()

