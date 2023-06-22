from http import HTTPStatus
from pydantic import BaseModel, Field


class BinanceModel(BaseModel):
    """Data model for the Binance"""
    id: int = Field(..., example=1)
    interval: str = Field(..., example='1h')
    symbol: str = Field(..., example='BTCUSDT')
    open_time: str = Field(..., example='2023-05-27 07:00:00')
    open: str = Field(..., example='26752.00000000')
    high: str = Field(..., example='26786.51000000')
    low: str = Field(..., example='26725.50000000')
    close: str = Field(..., example='26760.96000000')
    volume: str = Field(..., example='736.60810000')


class TickerPrice(BaseModel):
    symbol: str = Field(..., example='BTCUSDT')
    price: str = Field(..., example='4.00000200')


class ResponseCreateData(BaseModel):
    status: int = Field(..., example=HTTPStatus.OK)
    symbol: str = Field(..., example='BTCUSDT')
    interval: str = Field(..., example='1h')
