# Tradera Interaction / Automation
[![Type-Check](https://github.com/sdvnci/AsyncTradera/actions/workflows/mypy.yml/badge.svg?branch=main)](https://github.com/sdvnci/AsyncTradera/actions/workflows/mypy.yml)
[![Linting](https://github.com/sdvnci/AsyncTradera/actions/workflows/linting.yml/badge.svg?branch=main)](https://github.com/sdvnci/AsyncTradera/actions/workflows/linting.yml)
[![Tests](https://github.com/sdvnci/AsyncTradera/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/sdvnci/AsyncTradera/actions/workflows/tests.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Validation: Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://pydantic.dev)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

Async Python client for the [Tradera REST API (v4)](https://api.tradera.com/documentation) with an emphasis on typing.

Every endpoint in the v4 spec is wrapped, grouped into portals:

| Portal | Endpoints | Auth |
|--------|-----------|------|
| `ItemsPortal` | `/items` | App |
| `CategoriesPortal` | `/categories` | App |
| `SearchPortal` | `/search` | App |
| `ReferenceDataPortal` | `/reference-data` | App |
| `UsersPortal` | `/users` | App, User for `me` / `seller_info` / `payment_options` |
| `AuthPortal` | `/auth` | App for tokens, User+Seller for BankID |
| `OrdersPortal` | `/orders` | User+Seller |
| `ListingsPortal` | `/listings` (non-shop items, transactions, feedback) | User+Seller |
| `ShopPortal` | `/listings/shop-items`, `/listings/shop-settings` | User+Seller |
| `BuyerPortal` | `/buyer` | User |

## Install

### Manual

~~~bash
git clone git@github.com:sdvnci/AsyncTradera.git
cd AsyncTradera
pip install -r requirements.txt
~~~

## Quick Start

Create a connection, then pass it to the portal you want to use. Every portal method
returns `(status_code, payload)`, where the payload is either the typed response or a
`TraderaErrorResponse`.

~~~python
import asyncio

from AsyncTradera import SearchPortal, TraderaClient


async def main() -> None:
    connection = await TraderaClient.connect(
        app_id=1234,
        app_key="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
    )

    async with TraderaClient.scoped_client(connection=connection):
        status, result = await SearchPortal.search(connection, query="esp32")
        print(status, result)


if __name__ == "__main__":
    asyncio.run(main())
~~~

The library comes pre-configured with 'sensible' default values for connections, but you can configure these parameters by passing a `ConnectionConfig` object with the parameters you would like changed.

~~~python
config = ConnectionConfig(
    timeout=30,
    max_connections=20,
    max_keepalive_connections=10,
    http2=False,
    retries=4,
    user_agent="your_custom_UA_string",
)
connection = await TraderaClient.connect(
    app_id=1234,
    app_key="your_app_key",
    config=config,
)
~~~

**NOTE:** *A connection's config is tied to its identity. Two connections with the same credentials, if using different configs, will be treated as separate connections.*

## Acting as a User

App credentials (`X-App-Id` / `X-App-Key`) are enough for items, categories, search,
reference data and public user lookups. Orders, listings, the shop and buyer endpoints
also need a user token (`X-User-Id` / `X-User-Token`), so they need a *user connection*.

Calling a user endpoint on an app-only connection returns `401` locally, without a request.

### Getting a token

~~~python
from AsyncTradera import AuthPortal, TraderaClient

app = await TraderaClient.connect(app_id=APP_ID, app_key=APP_KEY)

secret_key = AuthPortal.new_secret_key()
print(AuthPortal.login_url(APP_ID, PUBLIC_KEY, secret_key))
# The user logs in on Tradera and authorizes your application...

status, token = await AuthPortal.fetch_token(app, user_id=USER_ID, secret_key=secret_key)
seller = await TraderaClient.connect_user(app, USER_ID, token["authToken"])
~~~

`PUBLIC_KEY` is the application's public key from the Developer Center, not the app key.
Store the token like a password and watch `hardExpirationTime`.

### Using a stored token

~~~python
from datetime import datetime, timedelta

from AsyncTradera import OrdersPortal, SellerOrderQueryDateMode, TraderaClient

async with TraderaClient.scoped_client(
    app_id=APP_ID,
    app_key=APP_KEY,
    user_id=USER_ID,
    user_token=USER_TOKEN,
) as seller:
    status, orders = await OrdersPortal.where(
        seller,
        from_date=datetime.now() - timedelta(days=1),
        query_date_mode=SellerOrderQueryDateMode.LAST_UPDATED_DATE,
    )
~~~

## Client Lifecycle

### Use the async context manager w/ existing connection object

Use `scoped_client()` when you want the connection lifecycle handled for you.

~~~python
connection = await TraderaClient.connect(app_id=APP_ID, app_key=APP_KEY)

async with TraderaClient.scoped_client(connection=connection):
    status, categories = await CategoriesPortal.all(connection)
~~~

### Use the async context manager w/o existing connection object

If you don't need to reuse the connection object, pass the credentials directly to `scoped_client()`.

~~~python
async with TraderaClient.scoped_client(app_id=APP_ID, app_key=APP_KEY) as connection:
    status, categories = await CategoriesPortal.all(connection)
~~~

### Start and close explicitly

Use `start()` and `close()` if you want to manage the lifecycle yourself.

~~~python
connection = await TraderaClient.connect(app_id=APP_ID, app_key=APP_KEY)

await TraderaClient.start(connection=connection)
try:
    status, categories = await CategoriesPortal.all(connection)
finally:
    await TraderaClient.close(connection=connection)
~~~

Connections are reference counted. Each `start()` / `scoped_client()` takes a reference
and each `close()` releases one; the HTTP client is only closed, and the connection
evicted from the pool, when the last reference is released. `close(force=True)` closes
immediately, and `TraderaClient.close_all()` force-closes everything at shutdown.

A connection that was never started still works: each request opens a client for its own
duration. Start the connection when making more than one request so they share a client.

## Concurrent Requests

A single connection is meant to be shared across concurrent requests.

~~~python
async with TraderaClient.scoped_client(connection=seller):
    results = await asyncio.gather(
        OrdersPortal.where(seller, from_date="2026-09-01"),
        ListingsPortal.seller_items(seller, filter_active=ActiveFilter.ACTIVE),
        ShopPortal.settings(seller),
    )

for status, data in results:
    if status == 200:
        print(f"Success :: {data}")
    else:
        print(f"Error :: {data}")
~~~

## Connection Lookup

If you need to retrieve a connection from the pool later, use `connection.uid`.

~~~python
connection = await TraderaClient.connect(app_id=APP_ID, app_key=APP_KEY)

async with TraderaClient.scoped_client(uid=connection.uid) as scoped_connection:
    status, time = await ReferenceDataPortal.time(scoped_connection)
~~~

## Errors

Tradera's error body is passed through with its real status code:

~~~json
{"error": {"code": "TooManyRequests", "message": "..."}}
~~~

Local failures (a user endpoint on an app-only connection, a transport error, a body
that is not JSON) use the same `TraderaErrorResponse` shape, so one check covers both.

Searches are the exception: invalid search parameters come back as a `200` with the
problems listed in `SearchResult["errors"]`.

## Identity Tagging

Pass `identity=True` to stamp each returned object with `__kind__` (its TypedDict name),
which helps when results from several portals end up in one collection.

## Listing Writes Are Queued

`ListingsPortal.add`, `ListingsPortal.restart` and the `ShopPortal` writes return a
`requestId`. Poll `ListingsPortal.request_results` to see whether each one was applied.

There is no sandbox: every call hits the live marketplace and sales are binding. To try
listing without publishing, add the item with `"autoCommit": False` and never call
`ListingsPortal.commit`, or end it straight away with `ListingsPortal.end`.

## Rate Limiting

Each method allows 10,000 calls per 24 hours by default. Past that, Tradera returns
`429 Too Many Requests`. Retrying won't help until the window resets, so the client
never retries 429s; `ConnectionConfig.retries` only covers failed connection attempts.

## Notes on the v4 Spec

- The v4 API is in beta. Endpoints and response shapes may change without notice.
- The OpenAPI spec leaves `User`, `Category`, `ItemStatus`, `IdDescriptionPair`,
  `SearchResult` and the search request bodies empty. Their types here come from the
  v3 SOAP WSDLs, which v4 mirrors in camelCase, and are marked `total=False`.
- The spec lists integer enum values without names. Member names come from the
  matching v3 WSDL enums, paired with the v4 values in declaration order.
- BankID, `BuyerPortal.buy` and feedback need activation by Tradera.
