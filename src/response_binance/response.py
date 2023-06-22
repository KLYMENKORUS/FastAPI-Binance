import logging
import io
from functools import wraps
from datetime import datetime
from typing import Optional, Any
from enum import Enum
import pandas as pd
from binance import AsyncClient
from config import API_KEY, API_SECRET
from database import async_session_maker, BinanceData, CSVData


class Interval(Enum):
    INTERVAL_1MINUTE = ('1m', AsyncClient.KLINE_INTERVAL_1MINUTE)
    INTERVAL_3MINUTE = ('3m', AsyncClient.KLINE_INTERVAL_3MINUTE)
    INTERVAL_5MINUTE = ('5m', AsyncClient.KLINE_INTERVAL_5MINUTE)
    INTERVAL_15MINUTE = ('15m', AsyncClient.KLINE_INTERVAL_15MINUTE)
    INTERVAL_30MINUTE = ('30m', AsyncClient.KLINE_INTERVAL_30MINUTE)
    INTERVAL_1HOUR = ('1h', AsyncClient.KLINE_INTERVAL_1HOUR)
    INTERVAL_2HOUR = ('2h', AsyncClient.KLINE_INTERVAL_2HOUR)
    INTERVAL_4HOUR = ('4h', AsyncClient.KLINE_INTERVAL_4HOUR)
    INTERVAL_6HOUR = ('6h', AsyncClient.KLINE_INTERVAL_6HOUR)
    INTERVAL_8HOUR = ('8h', AsyncClient.KLINE_INTERVAL_8HOUR)
    INTERVAL_12HOUR = ('12h', AsyncClient.KLINE_INTERVAL_12HOUR)
    INTERVAL_1DAY = ('1d', AsyncClient.KLINE_INTERVAL_1DAY)
    INTERVAL_3DAY = ('3d', AsyncClient.KLINE_INTERVAL_3DAY)
    INTERVAL_1WEEK = ('1w', AsyncClient.KLINE_INTERVAL_1WEEK)
    INTERVAL_1MONTH = ('1M', AsyncClient.KLINE_INTERVAL_1MONTH)


def with_connection_client(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        client = await AsyncClient.create(API_KEY, API_SECRET)
        result = await func(*args, client, **kwargs)
        await client.close_connection()
        return result
    return wrapper


class BinanceAPI:
    """
    Implementation class for getting current information
    by symbol and interval
    """

    @classmethod
    @with_connection_client
    async def get_account_balance(
            cls, asset: Optional[str], client: AsyncClient
    ) -> dict[str, Any]:
        """Returns information about the account for Binance"""
        return await client.get_asset_balance(asset=asset)

    @classmethod
    @with_connection_client
    async def get_klines(
            cls, symbol: Optional[str], intervals: Optional[str],
            client: AsyncClient
    ):
        """Get information about a Symbol from the Binance API"""
        result = [
            await client.get_klines(symbol=symbol, interval=interval.value[1])
            for interval in Interval if intervals == interval.value[0]
        ]

        return result

    @classmethod
    @with_connection_client
    async def get_symbol_ticker(cls, symbol: str, client: AsyncClient) -> dict[str, Any]:
        """Returns current price about a symbol"""
        return await client.get_symbol_ticker(symbol=symbol)

    @classmethod
    async def data_frame(cls, symbol: Optional[str], interval: Optional[str]) -> pd.DataFrame:
        """Packing in data frame"""
        result = await cls.get_klines(symbol, interval)

        df = pd.DataFrame(
            *result,
            columns=[
                'Open time', 'Open', 'High', 'Low', 'Close', 'Volume',
                'Close time', 'Quote asset volume',
                'Number of trades', 'Taker buy base asset volume',
                'Taker buy quote asset volume',
                'Ignore'
            ]
        )

        # Преобразование временных меток в удобный формат
        df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')

        # Удаление ненужных столбцов
        df = df.drop(
            [
                'Close time', 'Quote asset volume', 'Number of trades',
                'Taker buy base asset volume',
                'Taker buy quote asset volume', 'Ignore'
            ],
            axis=1)

        return df

    @classmethod
    async def write_to_csv_and_save_to_db(cls, symbol: Optional[str], interval: Optional[str]):
        """Write the data frame to a CSV file"""
        csv_buffer = io.StringIO()
        df = await cls.data_frame(symbol, interval)
        df.to_csv(csv_buffer, index=False)

        file_data = csv_buffer.getvalue().encode('utf8')

        async with async_session_maker() as session:
            await CSVData.create_csv_data(
                session, f'{symbol}-{interval}.csv',
                file_data
            )
            logging.info('Data saved successfully in database')
        csv_buffer.close()

    @classmethod
    async def create_data_in_db(cls, symbol: Optional[str], interval: Optional[str]):
        """Create a new data frame from the database"""
        result = await cls.get_klines(symbol, interval)

        async with async_session_maker() as session:
            create_data = [
                await BinanceData.create_binance_data(
                    session,
                    {
                        'interval': interval,
                        'symbol': symbol,
                        'open_time': str(datetime.fromtimestamp(data[0] / 1000)),
                        'open': str(data[1]),
                        'high': str(data[2]),
                        'low': str(data[3]),
                        'close': str(data[4]),
                        'volume': str(data[5])
                    })
                for res in result for data in res
            ]

        logging.info('Binance data created successfully')
        return create_data
