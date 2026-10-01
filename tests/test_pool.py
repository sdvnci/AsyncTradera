from asyncio import gather, sleep

import httpx
import pytest
import respx

from AsyncTradera import (
    ConnectionConfig,
    ReferenceDataPortal,
    TraderaClient,
    TraderaConnection,
)

from .conftest import APP_ID, APP_KEY, BASE, USER_ID, USER_TOKEN


async def test_connect_returns_the_pooled_connection_for_the_same_credentials() -> None:
    first = await TraderaClient.connect(app_id=APP_ID, app_key=APP_KEY)
    second = await TraderaClient.connect(app_id=APP_ID, app_key=APP_KEY)
    assert first is second
    assert await TraderaClient.get_connection(app_id=APP_ID, app_key=APP_KEY) is first


async def test_config_and_user_are_part_of_the_identity() -> None:
    base = await TraderaClient.connect(app_id=APP_ID, app_key=APP_KEY)
    tuned = await TraderaClient.connect(
        app_id=APP_ID, app_key=APP_KEY, config=ConnectionConfig(timeout=5)
    )
    user = await TraderaClient.connect(
        app_id=APP_ID, app_key=APP_KEY, user_id=USER_ID, user_token=USER_TOKEN
    )
    assert len({base.pool_key, tuned.pool_key, user.pool_key}) == 3
    assert not base.has_user and user.has_user


async def test_uid_is_a_lookup_handle_separate_from_the_credential_hash(
    app: TraderaConnection,
) -> None:
    assert app.uid != app.pool_key
    assert await TraderaClient.get_connection(uid=app.uid) is app
    assert await TraderaClient.connect(uid=app.uid) is app


async def test_connect_by_unknown_uid_without_credentials_raises() -> None:
    with pytest.raises(ValueError):
        await TraderaClient.connect(uid=42)


async def test_user_id_and_token_must_come_together() -> None:
    with pytest.raises(ValueError):
        TraderaConnection(APP_ID, APP_KEY, user_id=USER_ID)
    with pytest.raises(ValueError):
        TraderaConnection(APP_ID, APP_KEY, user_token=USER_TOKEN)


async def test_connect_user_reuses_app_credentials_and_config() -> None:
    config = ConnectionConfig(timeout=7)
    app = await TraderaClient.connect(app_id=APP_ID, app_key=APP_KEY, config=config)
    seller = await TraderaClient.connect_user(app, USER_ID, USER_TOKEN)
    assert seller.has_user and seller.user_id == USER_ID
    assert seller.config is config
    assert seller is await TraderaClient.connect(
        app_id=APP_ID,
        app_key=APP_KEY,
        user_id=USER_ID,
        user_token=USER_TOKEN,
        config=config,
    )


async def test_scoped_clients_share_one_reference_counted_client(
    app: TraderaConnection,
) -> None:
    async with TraderaClient.scoped_client(connection=app) as outer:
        assert outer is app and app.ref_count == 1 and app.is_active
        async with TraderaClient.scoped_client(app_id=APP_ID, app_key=APP_KEY) as inner:
            assert inner is app and app.ref_count == 2
        assert app.ref_count == 1 and app.is_active

    assert app.ref_count == 0 and not app.is_active
    assert await TraderaClient.get_connection(uid=app.uid) is None


async def test_starting_an_evicted_connection_puts_it_back_in_the_pool(
    app: TraderaConnection,
) -> None:
    async with TraderaClient.scoped_client(connection=app):
        pass
    assert await TraderaClient.get_connection(uid=app.uid) is None

    async with TraderaClient.scoped_client(connection=app):
        assert await TraderaClient.get_connection(uid=app.uid) is app


async def test_force_close_drops_every_reference(app: TraderaConnection) -> None:
    await TraderaClient.start(connection=app)
    await TraderaClient.start(connection=app)
    await TraderaClient.close(connection=app, force=True)
    assert app.ref_count == 0 and not app.is_active


@respx.mock
async def test_concurrent_requests_on_an_unstarted_connection_keep_the_client_open(
    app: TraderaConnection,
) -> None:
    arrivals: list[httpx.Request] = []
    open_while_in_flight: list[bool] = []

    async def staggered(request: httpx.Request) -> httpx.Response:
        arrivals.append(request)
        await sleep(0.01 * len(arrivals))
        open_while_in_flight.append(app.is_active)
        return httpx.Response(200, json="2026-10-01T12:00:00Z")

    respx.get(f"{BASE}/reference-data/time").mock(side_effect=staggered)
    results = await gather(*(ReferenceDataPortal.time(app) for _ in range(5)))

    assert [status for status, _ in results] == [200] * 5
    assert open_while_in_flight == [True] * 5
    assert app.ref_count == 0 and not app.is_active


async def test_debug_toggles_actually_change_state() -> None:
    try:
        assert TraderaClient.debug_on() is True and TraderaClient._debug is True
        assert TraderaClient.debug_off() is False and TraderaClient._debug is False
    finally:
        TraderaClient.debug_off()
