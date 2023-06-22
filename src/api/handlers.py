import logging
import io
from http import HTTPStatus
from typing import Annotated, List, Any
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from .schemas import BinanceModel, TickerPrice, ResponseCreateData
from database import get_async_session, BinanceData, CSVData
from response_binance import BinanceAPI
from binance.exceptions import BinanceAPIException
from fastapi_paginate import Page, paginate


router = APIRouter()


async def format_model_binance(result: list) -> List[BinanceModel]:
    """Format a list of Binance models"""
    return [
        BinanceModel(
            id=res.id,
            interval=res.interval,
            symbol=res.symbol,
            open_time=res.open_time,
            open=res.open,
            high=res.high,
            low=res.low,
            close=res.close,
            volume=res.volume
        )
        for res in result
    ]


@router.get('/generate/file')
async def generate_file(
        symbol: str, interval: str,
        background_tasks: BackgroundTasks,
        binance: BinanceAPI = Depends()) -> dict[str, Any]:
    """Generates a csv file and save in database"""
    try:
        background_tasks.add_task(
            binance.write_to_csv_and_save_to_db, symbol, interval)
        return {
            'status': HTTPStatus.OK,
            'detail': 'Is file generated successfully'
        }
    except BinanceAPIException as err:
        logging.error(err.message)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err.message
        )


@router.get('/download/file')
async def download_file(
        session: Annotated[AsyncSession, Depends(get_async_session)]
) -> Response:
    """Returns a FileResponse csv data"""
    try:
        data_csv = await CSVData.get_last_csv_data(session)
        content_type = io.BytesIO(data_csv[0].data).read()

        return Response(
            content=content_type,
            media_type='multipart/form-data',
            headers={'Content-Disposition': f'attachment; filename="{data_csv[0].filename}"'}
        )
    except IntegrityError as err:
        logging.error(f'Download file failed: {err}')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Download file failed'
        )


@router.get('/all_by_symbol', response_model=Page[BinanceModel])
async def get_all_by_symbol(
        session: Annotated[AsyncSession, Depends(get_async_session)],
        symbol: str = 'BTCUSDT'):
    """Returns all results by symbol"""
    try:
        result = await BinanceData.get_all_data_by_symbol(
            symbol, session
        )
        result = await format_model_binance(result)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Symbol {symbol} not found in database'
            )
        return paginate(result)

    except IntegrityError as err:
        logging.info(f'Error getting results for symbol {err}')
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='Database error')


@router.get('/ticker/price', response_model=TickerPrice)
async def get_ticker_price(
        symbol: str = 'BTCUSDT', binance: BinanceAPI = Depends()
) -> TickerPrice:
    """Returns the ticker price"""
    try:
        res = await binance.get_symbol_ticker(symbol)
        return TickerPrice(symbol=res.get('symbol'), price=res.get('price'))

    except BinanceAPIException as err:
        logging.error(err.message)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err.message
        )


@router.post('/create/data', response_model=ResponseCreateData)
async def create_data(
        background_tasks: BackgroundTasks,
        binance: BinanceAPI = Depends(),
        symbol: str = 'BTCUSDT', interval: str = '2h'
) -> ResponseCreateData:
    """Create a new data in the database"""
    try:
        background_tasks.add_task(
            binance.create_data_in_db, symbol, interval)

        return ResponseCreateData(
            status=HTTPStatus.OK,
            symbol=symbol,
            interval=interval,
        )
    except BinanceAPIException as err:
        logging.error(err.message)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err.message
        )
