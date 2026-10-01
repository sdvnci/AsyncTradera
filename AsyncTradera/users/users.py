from urllib.parse import quote

from ..common import (
    Endpoints,
    TraderaClient,
    TraderaConnection,
    TraderaErrorResponse,
    User,
)
from ._types import (
    GetFeedback,
    GetFeedbackRole,
    GetFeedbackRoles,
    GetFeedbackSummaryResponse,
    GetMemberPaymentOptionsResult,
    SellerInfo,
    UserInfo,
)

ENDPOINT = Endpoints.USERS.value


class UsersPortal(TraderaClient):
    """
    User lookups and feedback (app auth), plus the authenticated user's own
    profile and payment options (user auth).
    """

    @classmethod
    async def by_alias(
        cls: type["UsersPortal"],
        connection: TraderaConnection,
        alias: str,
        identity: bool = False,
    ) -> tuple[int, User | TraderaErrorResponse]:
        return await cls._send(
            connection,
            "GET",
            f"{ENDPOINT}/by-alias/{quote(alias, safe='')}",
            User,
            identity=identity,
        )

    @classmethod
    async def feedback(
        cls: type["UsersPortal"],
        connection: TraderaConnection,
        user_id: int,
        role: GetFeedbackRole | GetFeedbackRoles | None = None,
        max_number_of_items: int | None = None,
        identity: bool = False,
    ) -> tuple[int, list[GetFeedback] | TraderaErrorResponse]:
        return await cls._send(
            connection,
            "GET",
            f"{ENDPOINT}/{user_id}/feedback",
            list[GetFeedback],
            identity=identity,
            params={"role": role, "maxNumberOfItems": max_number_of_items},
        )

    @classmethod
    async def feedback_summary(
        cls: type["UsersPortal"],
        connection: TraderaConnection,
        user_id: int,
        identity: bool = False,
    ) -> tuple[int, GetFeedbackSummaryResponse | TraderaErrorResponse]:
        return await cls._send(
            connection,
            "GET",
            f"{ENDPOINT}/{user_id}/feedback/summary",
            GetFeedbackSummaryResponse,
            identity=identity,
        )

    @classmethod
    async def seller_info(
        cls: type["UsersPortal"],
        connection: TraderaConnection,
        user_id: int,
        identity: bool = False,
    ) -> tuple[int, SellerInfo | TraderaErrorResponse]:
        """
        Seller ratings and shop status for any user. Requires a user connection.
        """
        return await cls._send(
            connection,
            "GET",
            f"{ENDPOINT}/{user_id}/seller-info",
            SellerInfo,
            auth="user",
            identity=identity,
        )

    @classmethod
    async def me(
        cls: type["UsersPortal"],
        connection: TraderaConnection,
        identity: bool = False,
    ) -> tuple[int, UserInfo | TraderaErrorResponse]:
        """
        The profile of the user the connection acts as.
        """
        return await cls._send(
            connection,
            "GET",
            f"{ENDPOINT}/me",
            UserInfo,
            auth="user",
            identity=identity,
        )

    @classmethod
    async def payment_options(
        cls: type["UsersPortal"],
        connection: TraderaConnection,
        identity: bool = False,
    ) -> tuple[int, GetMemberPaymentOptionsResult | TraderaErrorResponse]:
        return await cls._send(
            connection,
            "GET",
            f"{ENDPOINT}/me/payment-options",
            GetMemberPaymentOptionsResult,
            auth="user",
            identity=identity,
        )


__all__ = ("UsersPortal",)
