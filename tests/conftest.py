from collections.abc import AsyncGenerator

import pytest

from AsyncTradera import TraderaClient, TraderaConnection

APP_ID = 1234
APP_KEY = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
USER_ID = 5678
USER_TOKEN = "user-token"
BASE = "https://api.tradera.com/v4"


@pytest.fixture(autouse=True)
async def clean_pool() -> AsyncGenerator[None, None]:
    yield
    await TraderaClient.close_all()


@pytest.fixture
async def app() -> TraderaConnection:
    return await TraderaClient.connect(app_id=APP_ID, app_key=APP_KEY)


@pytest.fixture
async def seller() -> TraderaConnection:
    return await TraderaClient.connect(
        app_id=APP_ID, app_key=APP_KEY, user_id=USER_ID, user_token=USER_TOKEN
    )
