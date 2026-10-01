from ..common import (
    ActiveFilter,
    ActiveFilters,
    DateLike,
    Endpoints,
    Item,
    TraderaClient,
    TraderaConnection,
    TraderaErrorResponse,
)
from ._types import BuyerTransaction, BuyResult

ENDPOINT = Endpoints.BUYER.value


class BuyerPortal(TraderaClient):
    """
    The authenticated user's purchases and wishlist. Every method needs a user connection.
    """

    @classmethod
    async def transactions(
        cls: type["BuyerPortal"],
        connection: TraderaConnection,
        min_transaction_date: DateLike | None = None,
        max_transaction_date: DateLike | None = None,
        identity: bool = False,
    ) -> tuple[int, list[BuyerTransaction] | TraderaErrorResponse]:
        """
        Purchases matched on creation date. Without ``min_transaction_date`` Tradera
        returns the last 60 days.
        """
        return await cls._send(
            connection,
            "GET",
            f"{ENDPOINT}/transactions",
            list[BuyerTransaction],
            auth="user",
            identity=identity,
            params={
                "minTransactionDate": min_transaction_date,
                "maxTransactionDate": max_transaction_date,
            },
        )

    @classmethod
    async def wishlist(
        cls: type["BuyerPortal"],
        connection: TraderaConnection,
        filter_active: ActiveFilter | ActiveFilters | None = None,
        min_end_date: DateLike | None = None,
        max_end_date: DateLike | None = None,
        identity: bool = False,
    ) -> tuple[int, list[Item] | TraderaErrorResponse]:
        return await cls._send(
            connection,
            "GET",
            f"{ENDPOINT}/wishlist",
            list[Item],
            auth="user",
            identity=identity,
            params={
                "filterActive": filter_active,
                "minEndDate": min_end_date,
                "maxEndDate": max_end_date,
            },
        )

    @classmethod
    async def buy(
        cls: type["BuyerPortal"],
        connection: TraderaConnection,
        item_id: int,
        buy_amount: int,
        identity: bool = False,
    ) -> tuple[int, BuyResult | TraderaErrorResponse]:
        """
        Buys an item at its Buy It Now price. This is a binding purchase and must be an
        explicit action by the user. Needs activation by Tradera.
        """
        return await cls._send(
            connection,
            "POST",
            f"{ENDPOINT}/buy",
            BuyResult,
            auth="user",
            identity=identity,
            json={"itemId": item_id, "buyAmount": buy_amount},
        )


__all__ = ("BuyerPortal",)
