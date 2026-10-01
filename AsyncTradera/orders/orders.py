from collections.abc import Sequence

from ..common import (
    APIError,
    DateLike,
    Endpoints,
    TraderaClient,
    TraderaConnection,
    TraderaErrorResponse,
)
from ._types import (
    FreightLabel,
    SellerOrder,
    SellerOrderQueryDateMode,
    SellerOrderQueryDateModes,
    SetSellerOrderAsShippedResponse,
    ShippingCode,
)

ENDPOINT = Endpoints.ORDERS.value
MAX_SHIPPING_CODE_IDS = 50


class OrdersPortal(TraderaClient):
    """
    The authenticated seller's orders. Every method needs a user connection.

    Orders are always real; there is no sandbox. Only mark an order as shipped once it
    has actually shipped.
    """

    @classmethod
    async def where(
        cls: type["OrdersPortal"],
        connection: TraderaConnection,
        from_date: DateLike | None = None,
        to_date: DateLike | None = None,
        query_date_mode: (
            SellerOrderQueryDateMode | SellerOrderQueryDateModes | None
        ) = None,
        identity: bool = False,
    ) -> tuple[int, list[SellerOrder] | TraderaErrorResponse]:
        """
        Orders created (or, with ``LAST_UPDATED_DATE``, updated) within a date range.
        """
        return await cls._send(
            connection,
            "GET",
            ENDPOINT,
            list[SellerOrder],
            auth="user",
            identity=identity,
            params={
                "fromDate": from_date,
                "toDate": to_date,
                "queryDateMode": query_date_mode,
            },
        )

    @classmethod
    async def get(
        cls: type["OrdersPortal"],
        connection: TraderaConnection,
        order_ids: int | Sequence[int],
        identity: bool = False,
    ) -> tuple[int, list[SellerOrder] | TraderaErrorResponse]:
        return await cls._send(
            connection,
            "GET",
            f"{ENDPOINT}/{cls._ids(order_ids)}",
            list[SellerOrder],
            auth="user",
            identity=identity,
        )

    @classmethod
    async def mark_shipped(
        cls: type["OrdersPortal"],
        connection: TraderaConnection,
        order_id: int,
        identity: bool = False,
    ) -> tuple[int, SetSellerOrderAsShippedResponse | TraderaErrorResponse]:
        return await cls._send(
            connection,
            "POST",
            f"{ENDPOINT}/{order_id}/ship",
            SetSellerOrderAsShippedResponse,
            auth="user",
            identity=identity,
        )

    @classmethod
    async def freight_labels(
        cls: type["OrdersPortal"],
        connection: TraderaConnection,
        order_ids: int | Sequence[int],
        identity: bool = False,
    ) -> tuple[int, list[FreightLabel] | TraderaErrorResponse]:
        return await cls._send(
            connection,
            "GET",
            f"{ENDPOINT}/{cls._ids(order_ids)}/freight-labels",
            list[FreightLabel],
            auth="user",
            identity=identity,
        )

    @classmethod
    async def shipping_codes(
        cls: type["OrdersPortal"],
        connection: TraderaConnection,
        order_ids: int | Sequence[int],
        identity: bool = False,
    ) -> tuple[int, list[ShippingCode] | TraderaErrorResponse]:
        """
        Parcel codes and drop-off QR codes for labelless shipping options.
        At most 50 orders per call.
        """
        if not isinstance(order_ids, int) and len(order_ids) > MAX_SHIPPING_CODE_IDS:
            return cls.parse_unknown_exception(
                APIError(
                    400,
                    f"shipping_codes accepts at most {MAX_SHIPPING_CODE_IDS} order ids, got {len(order_ids)}.",
                )
            )

        return await cls._send(
            connection,
            "GET",
            f"{ENDPOINT}/{cls._ids(order_ids)}/shipping-codes",
            list[ShippingCode],
            auth="user",
            identity=identity,
        )


__all__ = ("OrdersPortal",)
