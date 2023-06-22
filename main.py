import logging
import uvicorn
from fastapi import FastAPI
from api import router
from fastapi_paginate import add_pagination


app = FastAPI(title='Binance_API-service')

app.include_router(router, prefix='/crypto', tags=['crypto'])
add_pagination(app)


if __name__ == '__main__':
    logging.basicConfig(
        level='INFO'.upper(),
        format='%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    uvicorn.run(app, host='127.0.0.1', port=8000)

