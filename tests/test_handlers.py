import io
from http import HTTPStatus
from httpx import AsyncClient
from database import BinanceData, CSVData
from response_binance import BinanceAPI


async def test_create_data_in_db(async_session_test):
    """Test creating data in database"""
    data_test_info = {
        'interval': '1h',
        'symbol': 'BTCUSDT',
        'open_time': '2023-05-27 18:00:00',
        'open': '26666.87000000',
        'high': '26690.06000000',
        'low': '26636.98000000',
        'close': '26690.05000000',
        'volume': '519.80287000'
    }
    async with async_session_test() as session:
        created_data = await BinanceData.create_binance_data(
            session, data_test_info
        )
    assert created_data.symbol == data_test_info.get('symbol')
    assert created_data.interval == data_test_info.get('interval')


async def test_get_all_by_symbol(client: AsyncClient):
    """Test get_all_by_symbol"""
    response = await client.get('/crypto/all_by_symbol?symbol=BTCUSDT')
    assert response.status_code == HTTPStatus.OK
    assert response.json()['items'][0]['symbol'] == 'BTCUSDT'


async def test_not_found_symbol(client: AsyncClient):
    """Test a not found symbol"""
    response = await client.get('/crypto/all_by_symbol?symbol=ETHBTC')
    assert response.status_code == HTTPStatus.NOT_FOUND


async def test_get_ticker_price(client: AsyncClient):
    """Test get ticker price"""
    response = await client.get('/crypto/ticker/price?symbol=BTCUSDT')
    assert response.status_code == HTTPStatus.OK
    assert response.json()['symbol'] == 'BTCUSDT'
    assert len(response.json()) == 2


async def test_create_data_csv(async_session_test):
    """Test creating data CSV in database"""
    csv_buffer = io.StringIO()
    df = await BinanceAPI.data_frame('BTCUSDT', '2h')
    df.to_csv(csv_buffer, index=False)

    file_data = csv_buffer.getvalue().encode('utf8')

    async with async_session_test() as session:
        await CSVData.create_csv_data(
            session, 'BTCUSDT-2h.csv',
            file_data
        )
    csv_buffer.close()


async def test_generate_file(client: AsyncClient):
    """Test generate file"""
    response = await client.get('/crypto/generate/file?symbol=BTCUSDT&interval=6h')
    assert response.status_code == HTTPStatus.OK


async def test_download_file(client: AsyncClient):
    """Test download file"""
    response = await client.get('/crypto/download/file')
    assert response.status_code == HTTPStatus.OK


async def test_create_data(client: AsyncClient):
    """Test create data"""
    response = await client.post('/crypto/create/data?symbol=BTCUSDT&interval=4h')
    assert response.status_code == HTTPStatus.OK


