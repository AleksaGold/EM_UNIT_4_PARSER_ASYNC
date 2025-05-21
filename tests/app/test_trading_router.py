import pytest


@pytest.mark.asyncio
async def test_get_last_trading_dates(async_client, filled_spimex_data):
    """
    Тестирует эндпоинт /tradings/last-trading-dates.

    Проверяет, что:
    - возвращается статус 200;
    - ответ является списком;
    - возвращаемые даты входят в ожидаемый диапазон.
    """
    response = await async_client.get("/tradings/last-trading-dates?limit=2")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert set(response.json()).issubset(["2024-05-01", "2024-05-02"])


@pytest.mark.asyncio
async def test_get_dynamics(async_client, filled_spimex_data):
    """
    Тестирует эндпоинт /tradings/dynamics без фильтров.

    Проверяет, что:
    - возвращается статус 200;
    - ответ — список с двумя элементами;
    - даты торгов соответствуют указанному диапазону.
    """
    params = {"start_date": "2024-05-01", "end_date": "2024-05-02"}
    response = await async_client.get("/tradings/dynamics", params=params)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["date"] == "2024-05-01"
    assert data[1]["date"] == "2024-05-02"


@pytest.mark.asyncio
async def test_get_dynamics_with_filters(async_client, filled_spimex_data):
    """
    Тестирует эндпоинт /tradings/dynamics с фильтрацией по oil_id.

    Проверяет, что:
    - возвращается статус 200;
    - возвращён только один объект;
    - его oil_id соответствует фильтру.
    """
    params = {"start_date": "2024-05-01", "end_date": "2024-05-02", "oil_id": "oil_1"}
    response = await async_client.get("/tradings/dynamics", params=params)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["oil_id"] == "OIL_1"


@pytest.mark.asyncio
async def test_get_trading_results(async_client, filled_spimex_data):
    """
    Тестирует эндпоинт /tradings/trading-results без фильтров.

    Проверяет, что:
    - возвращается статус 200;
    - ответ — список нужной длины;
    - элементы отсортированы по убыванию даты.
    """
    params = {"limit": 2}
    response = await async_client.get("/tradings/trading-results", params=params)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["date"] >= data[1]["date"]


@pytest.mark.asyncio
async def test_get_trading_results_with_filters(async_client, filled_spimex_data):
    """
    Тестирует эндпоинт /tradings/trading-results с фильтрацией по oil_id.

    Проверяет, что:
    - возвращается статус 200;
    - все элементы в ответе имеют указанный oil_id.
    """
    params = {"oil_id": "oil_1", "limit": 5}
    response = await async_client.get("/tradings/trading-results", params=params)

    assert response.status_code == 200
    data = response.json()
    assert all(item["oil_id"] == "OIL_1" for item in data)
