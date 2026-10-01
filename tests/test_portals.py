from base64 import b64decode
from collections.abc import Iterator
from datetime import datetime
from json import loads
from typing import cast
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
import respx

from AsyncTradera import (
    AuthPortal,
    CategoriesPortal,
    IdDescriptionPair,
    ImageFormat,
    ListingsPortal,
    OrdersPortal,
    ReferenceDataPortal,
    SearchPortal,
    SearchResult,
    SellerOrderQueryDateMode,
    TraderaConnection,
    TraderaError,
    TraderaErrorResponse,
    UserInfo,
    UsersPortal,
)

from .conftest import APP_ID, APP_KEY, BASE, USER_ID, USER_TOKEN


@pytest.fixture(autouse=True)
def mock_api() -> Iterator[None]:
    with respx.mock:
        yield


def error_of(body: object) -> TraderaError:
    return cast(TraderaErrorResponse, body)["error"]


TRADERA_429 = {"error": {"code": "TooManyRequests", "message": "Rate limit exceeded"}}


async def test_app_connection_sends_only_app_headers(app: TraderaConnection) -> None:
    route = respx.get(f"{BASE}/categories").respond(json=[])
    await CategoriesPortal.all(app)

    headers = route.calls.last.request.headers
    assert headers["X-App-Id"] == str(APP_ID)
    assert headers["X-App-Key"] == APP_KEY
    assert "X-User-Id" not in headers and "X-User-Token" not in headers


async def test_user_connection_also_sends_user_headers(
    seller: TraderaConnection,
) -> None:
    route = respx.get(f"{BASE}/users/me").respond(json={"id": USER_ID})
    status, me = await UsersPortal.me(seller)

    assert status == 200 and cast(UserInfo, me)["id"] == USER_ID
    headers = route.calls.last.request.headers
    assert headers["X-User-Id"] == str(USER_ID)
    assert headers["X-User-Token"] == USER_TOKEN


async def test_user_endpoint_on_app_connection_fails_locally(
    app: TraderaConnection,
) -> None:
    route = respx.get(f"{BASE}/orders").respond(json=[])
    status, body = await OrdersPortal.where(app)

    assert status == 401
    assert error_of(body)["code"] == "Unauthorized"
    assert not route.called


async def test_tradera_errors_keep_their_status_and_body(
    app: TraderaConnection,
) -> None:
    respx.get(f"{BASE}/search").respond(429, json=TRADERA_429)
    assert await SearchPortal.search(app, query="esp32") == (429, TRADERA_429)


async def test_non_json_errors_are_wrapped_with_their_status(
    app: TraderaConnection,
) -> None:
    respx.get(f"{BASE}/categories").respond(502, text="<html>Bad Gateway</html>")
    status, body = await CategoriesPortal.all(app)

    assert status == 502
    assert error_of(body)["code"] == "502"
    assert "Bad Gateway" in error_of(body)["message"]


async def test_transport_failures_become_500_error_responses(
    app: TraderaConnection,
) -> None:
    respx.get(f"{BASE}/categories").mock(side_effect=httpx.ConnectError("refused"))
    status, body = await CategoriesPortal.all(app)

    assert status == 500
    assert "ConnectError" in error_of(body)["message"]


async def test_empty_success_bodies_decode_to_none(seller: TraderaConnection) -> None:
    respx.post(f"{BASE}/listings/items/77/commit").respond(200)
    assert await ListingsPortal.commit(seller, 77) == (200, None)


async def test_identity_tags_dicts_and_list_elements(app: TraderaConnection) -> None:
    respx.get(f"{BASE}/reference-data/counties").respond(
        json=[{"id": 1, "description": "Stockholm", "value": None}]
    )
    respx.get(f"{BASE}/search").respond(
        json={"totalNumberOfItems": 0, "totalNumberOfPages": 0, "items": []}
    )

    _, counties = await ReferenceDataPortal.counties(app, identity=True)
    _, result = await SearchPortal.search(app, query="x", identity=True)

    assert cast(list[IdDescriptionPair], counties)[0]["__kind__"] == "IdDescriptionPair"
    assert cast(SearchResult, result)["__kind__"] == "SearchResult"


@pytest.mark.parametrize(
    "payload", ["2026-10-01T12:00:00Z", {"time": "2026-10-01T12:00:00Z"}]
)
async def test_time_accepts_both_documented_shapes(
    app: TraderaConnection, payload: object
) -> None:
    respx.get(f"{BASE}/reference-data/time").respond(json=payload)
    assert await ReferenceDataPortal.time(app) == (200, "2026-10-01T12:00:00Z")


async def test_dates_and_enums_are_sent_as_wire_values(
    seller: TraderaConnection,
) -> None:
    route = respx.get(f"{BASE}/orders").respond(json=[])
    await OrdersPortal.where(
        seller,
        from_date=datetime(2026, 9, 1, 8, 30),
        query_date_mode=SellerOrderQueryDateMode.LAST_UPDATED_DATE,
    )

    query = parse_qs(urlsplit(str(route.calls.last.request.url)).query)
    assert query == {"fromDate": ["2026-09-01T08:30:00"], "queryDateMode": ["1"]}


async def test_id_lists_become_repeated_keys_or_comma_paths(
    seller: TraderaConnection,
) -> None:
    results = respx.get(f"{BASE}/listings/request-results").respond(json=[])
    orders = respx.get(f"{BASE}/orders/1,2,3").respond(json=[])

    await ListingsPortal.request_results(seller, [10, 11])
    await OrdersPortal.get(seller, [1, 2, 3])

    assert results.calls.last.request.url.query == b"requestIds=10&requestIds=11"
    assert orders.called


async def test_shipping_codes_rejects_more_than_50_orders(
    seller: TraderaConnection,
) -> None:
    status, _ = await OrdersPortal.shipping_codes(seller, range(51))
    assert status == 400


async def test_add_image_base64_encodes_the_bytes(seller: TraderaConnection) -> None:
    route = respx.post(f"{BASE}/listings/items/9/images").respond(200)
    await ListingsPortal.add_image(seller, 9, b"\x89PNG", ImageFormat.PNG)

    body = loads(route.calls.last.request.content)
    assert b64decode(body["imageData"]) == b"\x89PNG"
    assert body["imageFormat"] == 2 and body["hasMega"] is False


async def test_keyword_bodies_drop_unset_fields(seller: TraderaConnection) -> None:
    route = respx.put(f"{BASE}/listings/items/9/price").respond(
        json={"isSuccessful": True, "validationErrors": None}
    )
    await ListingsPortal.update_price(seller, 9, bin_price=250)
    assert loads(route.calls.last.request.content) == {"binPrice": 250}


async def test_fetch_token_posts_user_and_secret(app: TraderaConnection) -> None:
    token = {"authToken": "tok", "hardExpirationTime": "2027-01-01T00:00:00Z"}
    route = respx.post(f"{BASE}/auth/token").respond(json=token)

    assert await AuthPortal.fetch_token(app, USER_ID, "S" * 36) == (200, token)
    assert loads(route.calls.last.request.content) == {
        "userId": USER_ID,
        "secretKey": "S" * 36,
    }


def test_login_url_encodes_return_params() -> None:
    skey = AuthPortal.new_secret_key()
    url = AuthPortal.login_url(APP_ID, "pub", skey, {"next": "/orders?x=1"})
    query = parse_qs(urlsplit(url).query)

    assert url.startswith("https://api.tradera.com/token-login?")
    assert query["appId"] == [str(APP_ID)] and query["skey"] == [skey]
    assert parse_qs(query["ruparams"][0]) == {"next": ["/orders?x=1"]}

    with pytest.raises(ValueError):
        AuthPortal.login_url(APP_ID, "pub", "too-short")
