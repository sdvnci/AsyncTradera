from collections.abc import Mapping
from urllib.parse import urlencode
from uuid import uuid4

from ..common import (
    TOKEN_LOGIN_URL,
    Endpoints,
    TraderaClient,
    TraderaConnection,
    TraderaErrorResponse,
)
from ._types import (
    BeginBankIdOnFileVerificationResult,
    BeginBankIdVerificationResult,
    GetBankIdVerificationProgressResult,
    Token,
)

ENDPOINT = Endpoints.AUTH.value


class AuthPortal(TraderaClient):
    """
    The user token flow and BankID verification.

    Token flow:
        1. ``secret_key = AuthPortal.new_secret_key()``
        2. Send the user to ``AuthPortal.login_url(app_id, public_key, secret_key)``.
        3. After they authorize the app, ``AuthPortal.fetch_token(connection, user_id, secret_key)``.
        4. ``TraderaClient.connect_user(connection, user_id, token["authToken"])``.

    BankID methods need activation by Tradera before they can be called.
    """

    @staticmethod
    def new_secret_key() -> str:
        """
        A session secret (``skey``) for the token login. Tradera recommends a UUID.
        """
        return str(uuid4()).upper()

    @staticmethod
    def login_url(
        app_id: int,
        public_key: str,
        secret_key: str,
        return_params: Mapping[str, str] | None = None,
    ) -> str:
        """
        The Tradera page where a user logs in and authorizes the app.

        Args:
            app_id: The application id.
            public_key: The application's public key (``pkey``), not the app key.
            secret_key: The session secret (``skey``), 32-255 characters; keep it for ``fetch_token``.
            return_params: Optional values Tradera passes back on the accept URL redirect.
        """
        if not 32 <= len(secret_key) <= 255:
            raise ValueError("secret_key must be 32-255 characters long.")

        query: dict[str, str | int] = {
            "appId": app_id,
            "pkey": public_key,
            "skey": secret_key,
        }
        if return_params:
            query["ruparams"] = urlencode(return_params)
        return f"{TOKEN_LOGIN_URL}?{urlencode(query)}"

    @classmethod
    async def fetch_token(
        cls: type["AuthPortal"],
        connection: TraderaConnection,
        user_id: int,
        secret_key: str,
        identity: bool = False,
    ) -> tuple[int, Token | TraderaErrorResponse]:
        """
        Retrieves the token for a user who completed the token login with ``secret_key``.
        """
        return await cls._send(
            connection,
            "POST",
            f"{ENDPOINT}/token",
            Token,
            identity=identity,
            json={"userId": user_id, "secretKey": secret_key},
        )

    @classmethod
    async def bankid_begin(
        cls: type["AuthPortal"],
        connection: TraderaConnection,
        identity: bool = False,
    ) -> tuple[int, BeginBankIdVerificationResult | TraderaErrorResponse]:
        return await cls._send(
            connection,
            "POST",
            f"{ENDPOINT}/bankid/begin",
            BeginBankIdVerificationResult,
            auth="user",
            identity=identity,
        )

    @classmethod
    async def bankid_begin_on_file(
        cls: type["AuthPortal"],
        connection: TraderaConnection,
        identity: bool = False,
    ) -> tuple[int, BeginBankIdOnFileVerificationResult | TraderaErrorResponse]:
        return await cls._send(
            connection,
            "POST",
            f"{ENDPOINT}/bankid/begin-on-file",
            BeginBankIdOnFileVerificationResult,
            auth="user",
            identity=identity,
        )

    @classmethod
    async def bankid_progress(
        cls: type["AuthPortal"],
        connection: TraderaConnection,
        bank_id_order_ref: str,
        identity: bool = False,
    ) -> tuple[int, GetBankIdVerificationProgressResult | TraderaErrorResponse]:
        return await cls._send(
            connection,
            "GET",
            f"{ENDPOINT}/bankid/progress",
            GetBankIdVerificationProgressResult,
            auth="user",
            identity=identity,
            params={"bankIdOrderRef": bank_id_order_ref},
        )

    @classmethod
    async def bankid_cancel(
        cls: type["AuthPortal"],
        connection: TraderaConnection,
        bank_id_order_ref: str,
    ) -> tuple[int, None | TraderaErrorResponse]:
        return await cls._send(
            connection,
            "POST",
            f"{ENDPOINT}/bankid/cancel",
            type(None),
            auth="user",
            json={"bankIdOrderRef": bank_id_order_ref},
        )


__all__ = ("AuthPortal",)
