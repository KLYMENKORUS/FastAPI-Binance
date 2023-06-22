import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
DB_NAME = os.getenv('POSTGRES_DB')
DB_PASS = os.getenv('POSTGRES_PASSWORD')
DB_USER = os.getenv('POSTGRES_USER')
DB_PORT = os.getenv('POSTGRES_PORT')
DB_HOST = os.getenv('POSTGRES_HOST')

DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
DATABASE_URL_TEST = 'postgresql+asyncpg://postgres_test:postgres_test@127.0.0.1:5436/BinanceAPITest'
