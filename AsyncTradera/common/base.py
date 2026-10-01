from base64 import b64encode
from contextlib import asynccontextmanager
from dataclasses import dataclass, fields
from datetime import date, datetime
from enum import Enum
from hashlib import sha256
from json import JSONDecodeError, dumps
from logging import DEBUG, ERROR, INFO, WARNING, Logger, getLogger
from threading import Lock
from typing import (
    Any,
    AsyncGenerator,
    ClassVar,
    Final,
    Literal,
    Mapping,
    Sequence,
    TypeVar,
    cast,
    get_args,
    get_origin,
)
from uuid import uuid4

from httpx import AsyncClient, AsyncHTTPTransport, Limits, Response
from pydantic import SecretStr

from ._types import (
    AuthLevels,
    DateLike,
    QueryScalar,
    QueryValue,
    Taggable,
    TraderaErrorResponse,
    TraderaStatusCode,
)

LOGGER: Logger = getLogger("AsyncTradera")
VERSION: Final[str] = "0.1.0.0"
TOKEN_LOGIN_URL: Final[str] = "https://api.tradera.com/token-login"
SUCCESS_STATUSES: Final[tuple[int, ...]] = (200, 201, 202, 204)
T = TypeVar("T")

HTTPMethods = Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]


class APIError(Exception):
    """
    Raised for local failures such as calling a user endpoint without user credentials.
    Portals convert it to a ``TraderaErrorResponse`` carrying ``status_code``.
    """

    __slots__ = ("status_code", "details")

    def __init__(self, status: int, detail: str) -> None:
        super().__init__(status, detail)
        self.status_code = status
        self.details = detail

    def json(self) -> TraderaErrorResponse:
        return {
            "error": {
                "code": TraderaStatusCode.label(self.status_code),
                "message": self.details,
            }
        }

    def __str__(self) -> str:
        outdict = {
            "status_code": self.status_code,
            "details": self.json(),
        }
        return dumps(outdict, indent=4, ensure_ascii=False)

    @property
    def text(self) -> str:
        return self.__str__()

    @property
    def content(self) -> bytes:
        return self.__str__().encode("utf-8")


class Loggable:
    __slots__ = ()
    _debug: ClassVar[bool] = False

    @classmethod
    def debug_on(cls: "type[Loggable]") -> bool:
        """
        Enables logging for this class and all subclasses that have not set their own state.
        Returns:
            bool: The new debug state (True).
        """
        cls._debug = True
        return cls._debug

    @classmethod
    def debug_off(cls: "type[Loggable]") -> bool:
        """
        Disables logging for this class and all subclasses that have not set their own state.
        Returns:
            bool: The new debug state (False).
        """
        cls._debug = False
        return cls._debug

    @classmethod
    def log(
        cls: "type[Loggable]", message: str, level: Literal[10, 20, 30, 40] = INFO
    ) -> None:
        """
        Logs a message at the specified level if debugging is enabled.
        Args:
            message (str): The message to log.
            level (Literal[10, 20, 30, 40], optional): The logging level (DEBUG=10, INFO=20, WARNING=30, ERROR=40). Defaults to INFO.
        """
        if cls._debug:
            LOGGER.log(level, message)

    @classmethod
    def debug(cls: "type[Loggable]", message: str) -> None:
        cls.log(message, level=DEBUG)

    @classmethod
    def info(cls: "type[Loggable]", message: str) -> None:
        cls.log(message, level=INFO)

    @classmethod
    def warning(cls: "type[Loggable]", message: str) -> None:
        cls.log(message, level=WARNING)

    @classmethod
    def error(cls: "type[Loggable]", message: str) -> None:
        cls.log(message, level=ERROR)


@dataclass(slots=True, frozen=True)
class ConnectionConfig:
    """
    Transport settings for a connection. Part of the connection's identity: the same
    credentials with a different config are pooled as a separate connection.

    ``retries`` is the number of connect-level retries on the httpx transport. HTTP 429
    is never retried; Tradera's limit is 10,000 calls per method per 24 hours.
    """

    timeout: float = 500
    max_connections: int = 20
    max_keepalive_connections: int = 10
    http2: bool = False
    retries: int = 4
    user_agent: str = f"AsyncTradera/{VERSION}"
    endpoint: str = "https://api.tradera.com/v4"

    def __hash__(self: "ConnectionConfig") -> int:
        raw = ":".join(f"{f.name}={getattr(self, f.name)}" for f in fields(self))
        digest = int.from_bytes(
            sha256(raw.encode("utf-8")).digest()[:8], "big", signed=True
        )
        return -2 if digest == -1 else digest


class TraderaConnection:
    """
    One set of Tradera credentials and the httpx client that serves them.

    App credentials (``X-App-Id`` / ``X-App-Key``) are always sent. When ``user_id``
    and ``user_token`` are given, the connection also acts as that user and can reach
    the "User" and "User+Seller" endpoints.

    The client is reference counted: every ``start()`` takes a reference, every
    ``close()`` releases one, and the client is closed when the count reaches zero.
    """

    __slots__ = (
        "_app_id",
        "_app_key",
        "_user_id",
        "_user_token",
        "_config",
        "_lock",
        "_client",
        "_ref_count",
        "_pool_key",
        "_uid",
    )

    def __init__(
        self: "TraderaConnection",
        app_id: int,
        app_key: str,
        user_id: int | None = None,
        user_token: str | None = None,
        config: ConnectionConfig | None = None,
    ) -> None:
        if not app_id:
            raise ValueError("app_id must be a non-zero integer.")
        if not app_key:
            raise ValueError("app_key must be a non-empty string.")
        if (user_id is None) != (not user_token):
            raise ValueError("user_id and user_token must be provided together.")

        self._app_id: int = app_id
        self._app_key: SecretStr = SecretStr(app_key)
        self._user_id: int | None = user_id
        self._user_token: SecretStr | None = (
            SecretStr(user_token) if user_token else None
        )
        self._config: ConnectionConfig = config or ConnectionConfig()
        self._pool_key: int = self.hash(
            app_id, app_key, user_id, user_token, self._config
        )
        self._lock: Lock = Lock()
        self._client: AsyncClient | None = None
        self._ref_count: int = 0
        self._uid: int = uuid4().int

    def _headers(self: "TraderaConnection") -> dict[str, str]:
        headers = {
            "User-Agent": self._config.user_agent,
            "Accept": "application/json",
            "X-App-Id": str(self._app_id),
            "X-App-Key": self._app_key.get_secret_value(),
        }
        if self._user_id is not None and self._user_token is not None:
            headers["X-User-Id"] = str(self._user_id)
            headers["X-User-Token"] = self._user_token.get_secret_value()
        return headers

    def _build_client(self: "TraderaConnection") -> AsyncClient:
        return AsyncClient(
            base_url=self._config.endpoint,
            headers=self._headers(),
            timeout=self._config.timeout,
            transport=AsyncHTTPTransport(
                retries=self._config.retries,
                http2=self._config.http2,
                limits=Limits(
                    max_connections=self._config.max_connections,
                    max_keepalive_connections=self._config.max_keepalive_connections,
                ),
            ),
        )

    async def start(self: "TraderaConnection") -> None:
        with self._lock:
            if self._client is None or self._client.is_closed:
                self._client = self._build_client()
            self._ref_count += 1

    async def close(self: "TraderaConnection", force: bool = False) -> None:
        """
        Releases one reference, closing the client when none remain.
        ``force=True`` closes immediately and resets the count to zero.
        """
        stale: AsyncClient | None = None
        with self._lock:
            self._ref_count = max(0, self._ref_count - 1)
            if self._ref_count == 0 or force:
                self._ref_count = 0
                stale, self._client = self._client, None

        if stale is not None:
            await stale.aclose()

    async def request(
        self: "TraderaConnection",
        method: HTTPMethods,
        url: str,
        **kwargs: Any,
    ) -> Response:
        """
        Sends a request on this connection's client. The request holds its own reference
        for its duration, so a connection that was never started still works (a client is
        opened and closed around the call), and concurrent requests never close the client
        out from under each other.
        """
        await self.start()
        try:
            client = self._client
            if client is None:
                raise APIError(500, "HTTP client could not be initialized.")
            return await client.request(method, url, **kwargs)
        finally:
            await self.close()

    @property
    def app_id(self: "TraderaConnection") -> int:
        return self._app_id

    @property
    def app_key(self: "TraderaConnection") -> SecretStr:
        return self._app_key

    @property
    def user_id(self: "TraderaConnection") -> int | None:
        return self._user_id

    @property
    def user_token(self: "TraderaConnection") -> SecretStr | None:
        return self._user_token

    @property
    def has_user(self: "TraderaConnection") -> bool:
        return self._user_id is not None and self._user_token is not None

    @property
    def config(self: "TraderaConnection") -> ConnectionConfig:
        return self._config

    @property
    def endpoint(self: "TraderaConnection") -> str:
        return self._config.endpoint

    @property
    def ref_count(self: "TraderaConnection") -> int:
        return self._ref_count

    @property
    def is_active(self: "TraderaConnection") -> bool:
        return self._client is not None and not self._client.is_closed

    @property
    def uid(self: "TraderaConnection") -> int:
        return self._uid

    @property
    def pool_key(self: "TraderaConnection") -> int:
        return self._pool_key

    def __eq__(self: "TraderaConnection", other: object) -> bool:
        if not isinstance(other, TraderaConnection):
            return NotImplemented
        return (
            self._app_id == other._app_id
            and self._app_key == other._app_key
            and self._user_id == other._user_id
            and self._user_token == other._user_token
            and self._config == other._config
        )

    @staticmethod
    def hash(
        app_id: int,
        app_key: str,
        user_id: int | None,
        user_token: str | None,
        config: ConnectionConfig,
    ) -> int:
        raw = f"{app_id}:{app_key}:{user_id or ''}:{user_token or ''}:{hash(config)}"
        digest = int.from_bytes(
            sha256(raw.encode("utf-8")).digest()[:8], "big", signed=True
        )
        return -2 if digest == -1 else digest

    def __hash__(self: "TraderaConnection") -> int:
        return self._pool_key


class TraderaClient(Loggable):
    __slots__ = ()

    _physical_pool: ClassVar[dict[int, TraderaConnection]] = {}
    """
    The pool of all connection objects, where the key is the hashed credentials + config.
    """
    _virtual_pool: ClassVar[dict[int, int]] = {}
    """
    A dict of "virtual" addresses which map to the "physical" hashes of each value.
    This gives a layer of abstraction between the uuid provided to the user, and the
    actual physical hash of an object.
    """

    _pool_lock: ClassVar[Lock] = Lock()
    """
    Guards the pools. Critical sections never await, so a thread lock is safe here and,
    unlike an asyncio lock, is not tied to the event loop that first contended for it.
    """

    @staticmethod
    def _apply_identity_tag(
        payload: object,
        return_type: object,
    ) -> object:
        if isinstance(payload, dict):
            name = getattr(return_type, "__name__", None)
            if name:
                cast(Taggable, payload)["__kind__"] = name

        elif isinstance(payload, list) and get_origin(return_type) is list:
            args = get_args(return_type)
            name = getattr(args[0], "__name__", None) if args else None
            if name:
                for element in payload:
                    if isinstance(element, dict):
                        cast(Taggable, element)["__kind__"] = name

        return payload

    @classmethod
    def validate_response(
        cls: type["TraderaClient"],
        res: Response,
        accepted_statuses: tuple[int, ...],
        return_type: type[T],
        identity: bool = False,
    ) -> tuple[int, TraderaErrorResponse | T]:
        """
        Decodes a response into ``(status, payload)``. Never raises: Tradera error bodies
        are passed through with their real status, and anything else that is not a
        successful JSON (or empty) body is wrapped in a ``TraderaErrorResponse``.
        """
        payload: object = None
        if res.content:
            try:
                payload = res.json()
            except (JSONDecodeError, UnicodeDecodeError) as e:
                status = (
                    500 if res.status_code in accepted_statuses else res.status_code
                )
                return (
                    status,
                    APIError(
                        status,
                        f"Could not decode response body: {e}. Raw response: {res.text[:500]}",
                    ).json(),
                )

        if res.status_code not in accepted_statuses:
            if isinstance(payload, dict) and isinstance(payload.get("error"), dict):
                return res.status_code, cast(TraderaErrorResponse, payload)

            detail = (
                payload
                if isinstance(payload, str)
                else (dumps(payload) if payload is not None else res.reason_phrase)
            )
            return res.status_code, APIError(res.status_code, detail).json()

        if identity:
            payload = cls._apply_identity_tag(payload, return_type)

        return res.status_code, cast(T, payload)

    @staticmethod
    def parse_unknown_exception(
        exception: Exception,
    ) -> tuple[int, TraderaErrorResponse]:
        """
        Parses an exception and returns a standardized error response.
        Args:
            exception (Exception): The exception to parse.
        Returns:
            tuple[int, TraderaErrorResponse]: The APIError's status (500 for any other exception) and the error details.
        """
        if isinstance(exception, APIError):
            return exception.status_code, exception.json()

        return 500, APIError(500, f"{type(exception).__name__}: {exception}").json()

    @staticmethod
    def _query_value(value: QueryScalar) -> str | int | float | bool | None:
        if isinstance(value, Enum):
            return cast(str | int, value.value)
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        return value

    @classmethod
    def _query(
        cls: type["TraderaClient"], params: Mapping[str, QueryValue]
    ) -> dict[str, Any]:
        """
        Drops unset parameters and converts dates and enums to their wire values.
        Sequences become repeated keys (``?ids=1&ids=2``), which is how the API binds arrays.
        """
        out: dict[str, Any] = {}
        for key, value in params.items():
            if value is None:
                continue
            if isinstance(value, Sequence) and not isinstance(value, str):
                out[key] = [cls._query_value(v) for v in value if v is not None]
            else:
                out[key] = cls._query_value(value)
        return out

    @staticmethod
    def _compact(body: Mapping[str, object]) -> dict[str, object]:
        """
        Drops top-level ``None`` values from a request body built from keyword arguments.
        """
        return {k: v for k, v in body.items() if v is not None}

    @staticmethod
    def _iso(value: DateLike) -> str:
        return value if isinstance(value, str) else value.isoformat()

    @staticmethod
    def _b64(data: bytes) -> str:
        return b64encode(data).decode("ascii")

    @staticmethod
    def _ids(ids: int | Sequence[int]) -> str:
        """
        Formats one or more ids as the comma-separated path segment Tradera expects.
        """
        return str(ids) if isinstance(ids, int) else ",".join(str(i) for i in ids)

    @classmethod
    async def _send(
        cls: type["TraderaClient"],
        connection: TraderaConnection,
        method: HTTPMethods,
        path: str,
        return_type: type[T],
        auth: AuthLevels = "app",
        identity: bool = False,
        params: Mapping[str, QueryValue] | None = None,
        json: object = None,
        accepted_statuses: tuple[int, ...] = SUCCESS_STATUSES,
    ) -> tuple[int, T | TraderaErrorResponse]:
        """
        The shared request path for every portal method: checks the auth level the
        endpoint needs, sends the request, and normalizes the result.
        """
        if auth == "user" and not connection.has_user:
            return cls.parse_unknown_exception(
                APIError(
                    401,
                    f"{method} /{path} requires user authorization. Connect with user_id and user_token.",
                )
            )

        kwargs: dict[str, Any] = {}
        if params:
            kwargs["params"] = cls._query(params)
        if json is not None:
            kwargs["json"] = json

        try:
            res = await connection.request(
                method, f"{connection.endpoint}/{path}", **kwargs
            )
            return cls.validate_response(
                res, accepted_statuses, return_type, identity=identity
            )
        except Exception as e:
            cls.error(f"_send:::{method} /{path} failed with {e!r}")
            return cls.parse_unknown_exception(e)

    @classmethod
    def _register(
        cls: type["TraderaClient"], connection: TraderaConnection
    ) -> TraderaConnection:
        """
        Adds a connection to the pool unless one with the same credentials and config is
        already there, and returns whichever connection the pool holds for that key.
        """
        with cls._pool_lock:
            pooled = cls._physical_pool.setdefault(connection.pool_key, connection)
            cls._virtual_pool[pooled.uid] = pooled.pool_key

        if pooled is connection:
            cls.info(f"_register:::Connection with uid {connection.uid} added to pool")
        return pooled

    @classmethod
    async def evict_connection(cls: type["TraderaClient"], uid: int) -> None:
        with cls._pool_lock:
            physical_addr = cls._virtual_pool.pop(uid, None)
            if physical_addr is None:
                cls.info(
                    f"evict_connection:::Could not find any connection with uuid {uid}"
                )
                return

            pooled = cls._physical_pool.get(physical_addr)
            if pooled is not None and pooled.uid == uid:
                del cls._physical_pool[physical_addr]

        cls.info(f"evict_connection:::Connection with uuid {uid} evicted from pool")

    @classmethod
    async def get_connection(
        cls: type["TraderaClient"],
        uid: int | None = None,
        app_id: int | None = None,
        app_key: str | None = None,
        user_id: int | None = None,
        user_token: str | None = None,
        config: ConnectionConfig | None = None,
    ) -> TraderaConnection | None:
        """
        Looks up a pooled connection by ``uid``, or by credentials + config
        (the default config when none is given).
        """
        with cls._pool_lock:
            if uid is not None:
                physical = cls._virtual_pool.get(uid, None)
                if physical is None:
                    cls.info(
                        f"get_connection:::No connection object with uuid {uid} found."
                    )
                    return None
                return cls._physical_pool.get(physical, None)

            if app_id and app_key:
                physical = TraderaConnection.hash(
                    app_id, app_key, user_id, user_token, config or ConnectionConfig()
                )
                return cls._physical_pool.get(physical, None)

            return None

    @classmethod
    async def connect(
        cls: type["TraderaClient"],
        uid: int | None = None,
        app_id: int | None = None,
        app_key: str | None = None,
        user_id: int | None = None,
        user_token: str | None = None,
        config: ConnectionConfig | None = None,
    ) -> TraderaConnection:
        """
        Returns the pooled connection for these credentials, creating it if needed.
        Connecting twice with the same credentials and config returns the same object.
        """
        found = await cls.get_connection(
            uid, app_id, app_key, user_id, user_token, config
        )
        if found is not None:
            return found

        if uid is not None and not (app_id and app_key):
            raise ValueError(
                f"No pooled connection with uid {uid}, and no credentials to create one."
            )

        return cls._register(
            TraderaConnection(
                app_id=app_id or 0,
                app_key=app_key or "",
                user_id=user_id,
                user_token=user_token,
                config=config,
            )
        )

    @classmethod
    async def connect_user(
        cls: type["TraderaClient"],
        connection: TraderaConnection,
        user_id: int,
        user_token: str,
    ) -> TraderaConnection:
        """
        Returns the pooled connection acting as ``user_id``, reusing the app credentials
        and config of an existing connection. Typical after ``AuthPortal.fetch_token``.
        """
        return await cls.connect(
            app_id=connection.app_id,
            app_key=connection.app_key.get_secret_value(),
            user_id=user_id,
            user_token=user_token,
            config=connection.config,
        )

    @classmethod
    async def start(
        cls: type["TraderaClient"],
        uid: int | None = None,
        app_id: int | None = None,
        app_key: str | None = None,
        user_id: int | None = None,
        user_token: str | None = None,
        connection: TraderaConnection | None = None,
        config: ConnectionConfig | None = None,
    ) -> TraderaConnection:
        if connection is None:
            connection = await cls.connect(
                uid, app_id, app_key, user_id, user_token, config
            )
        else:
            cls._register(connection)

        await connection.start()
        return connection

    @classmethod
    async def close(
        cls: type["TraderaClient"],
        uid: int | None = None,
        app_id: int | None = None,
        app_key: str | None = None,
        user_id: int | None = None,
        user_token: str | None = None,
        connection: TraderaConnection | None = None,
        config: ConnectionConfig | None = None,
        force: bool = False,
    ) -> None:
        """
        Releases one reference on a connection.

        The client is only closed, and the connection evicted from the pool, when no
        references remain. Pass ``force=True`` to close unconditionally.
        """
        conn = (
            connection
            if connection is not None
            else await cls.get_connection(
                uid, app_id, app_key, user_id, user_token, config
            )
        )

        if conn is None:
            raise ValueError(
                "No connection found to close. Provide a valid connection, uid, or credentials."
            )

        await conn.close(force=force)
        if conn.ref_count == 0:
            await cls.evict_connection(conn.uid)

    @classmethod
    async def close_all(cls: type["TraderaClient"]) -> None:
        """
        Force-closes every pooled connection and empties the pool. Meant for shutdown.
        """
        with cls._pool_lock:
            connections = list(cls._physical_pool.values())
            cls._physical_pool.clear()
            cls._virtual_pool.clear()

        for conn in connections:
            await conn.close(force=True)

    @classmethod
    @asynccontextmanager
    async def scoped_client(
        cls: type["TraderaClient"],
        uid: int | None = None,
        app_id: int | None = None,
        app_key: str | None = None,
        user_id: int | None = None,
        user_token: str | None = None,
        connection: TraderaConnection | None = None,
        config: ConnectionConfig | None = None,
    ) -> AsyncGenerator[TraderaConnection, None]:
        connection = await cls.start(
            uid=uid,
            app_id=app_id,
            app_key=app_key,
            user_id=user_id,
            user_token=user_token,
            connection=connection,
            config=config,
        )

        try:
            yield connection
        finally:
            await cls.close(connection=connection)

    @classmethod
    async def request(
        cls: type["TraderaClient"],
        method: HTTPMethods,
        url: str,
        connection: TraderaConnection | None = None,
        uid: int | None = None,
        **kwargs: Any,
    ) -> Response:
        if connection is None:
            if uid is None:
                raise ValueError("Either a connection or uid must be provided.")
            connection = await cls.get_connection(uid=uid)
            if not connection:
                raise ValueError(
                    "No connection found for the provided uid. A connection must be started before making requests."
                )

        return await connection.request(method, url, **kwargs)


__all__ = (
    "LOGGER",
    "VERSION",
    "TOKEN_LOGIN_URL",
    "SUCCESS_STATUSES",
    "HTTPMethods",
    "APIError",
    "Loggable",
    "ConnectionConfig",
    "TraderaConnection",
    "TraderaClient",
)
