from collections.abc import Sequence

from ..common import (
    Endpoints,
    QueuedRequestResponse,
    TraderaClient,
    TraderaConnection,
    TraderaErrorResponse,
)
from ._types import (
    SetActivateDateOnShopItemsResult,
    SetActivateDateShopItem,
    SetPriceOnShopItemsResult,
    SetPriceShopItem,
    SetQuantityOnShopItemsResult,
    SetQuantityShopItem,
    ShopItemData,
    ShopItemVariantData,
    ShopSettingsData,
)

ENDPOINT = f"{Endpoints.LISTINGS.value}/shop-items"
SETTINGS = f"{Endpoints.LISTINGS.value}/shop-settings"


class ShopPortal(TraderaClient):
    """
    The authenticated seller's shop items and shop settings. Every method needs a
    user connection, and the seller needs a Tradera shop.

    Adds, updates, removals and price changes are queued: poll the returned
    ``requestId`` values with ``ListingsPortal.request_results``. Quantity changes
    apply without a result to check.
    """

    @classmethod
    async def add(
        cls: type["ShopPortal"],
        connection: TraderaConnection,
        item: ShopItemData,
        identity: bool = False,
    ) -> tuple[int, QueuedRequestResponse | TraderaErrorResponse]:
        return await cls._send(
            connection,
            "POST",
            ENDPOINT,
            QueuedRequestResponse,
            auth="user",
            identity=identity,
            json=item,
        )

    @classmethod
    async def update(
        cls: type["ShopPortal"],
        connection: TraderaConnection,
        item_id: int,
        item: ShopItemData,
        identity: bool = False,
    ) -> tuple[int, QueuedRequestResponse | TraderaErrorResponse]:
        return await cls._send(
            connection,
            "PUT",
            ENDPOINT,
            QueuedRequestResponse,
            auth="user",
            identity=identity,
            json={"itemId": item_id, "itemData": item},
        )

    @classmethod
    async def add_variant(
        cls: type["ShopPortal"],
        connection: TraderaConnection,
        item: ShopItemVariantData,
        identity: bool = False,
    ) -> tuple[int, QueuedRequestResponse | TraderaErrorResponse]:
        return await cls._send(
            connection,
            "POST",
            f"{ENDPOINT}/variant",
            QueuedRequestResponse,
            auth="user",
            identity=identity,
            json=item,
        )

    @classmethod
    async def update_variant(
        cls: type["ShopPortal"],
        connection: TraderaConnection,
        item_id: int,
        item: ShopItemVariantData,
        identity: bool = False,
    ) -> tuple[int, QueuedRequestResponse | TraderaErrorResponse]:
        return await cls._send(
            connection,
            "PUT",
            f"{ENDPOINT}/variant",
            QueuedRequestResponse,
            auth="user",
            identity=identity,
            json={"itemId": item_id, "itemData": item},
        )

    @classmethod
    async def remove(
        cls: type["ShopPortal"],
        connection: TraderaConnection,
        item_id: int,
        identity: bool = False,
    ) -> tuple[int, QueuedRequestResponse | TraderaErrorResponse]:
        """
        Removes a shop item by moving its end date into the past.
        """
        return await cls._send(
            connection,
            "DELETE",
            f"{ENDPOINT}/{item_id}",
            QueuedRequestResponse,
            auth="user",
            identity=identity,
        )

    @classmethod
    async def set_prices(
        cls: type["ShopPortal"],
        connection: TraderaConnection,
        items: Sequence[SetPriceShopItem],
        identity: bool = False,
    ) -> tuple[int, SetPriceOnShopItemsResult | TraderaErrorResponse]:
        return await cls._send(
            connection,
            "PUT",
            f"{ENDPOINT}/prices",
            SetPriceOnShopItemsResult,
            auth="user",
            identity=identity,
            json={"shopItems": list(items)},
        )

    @classmethod
    async def set_quantities(
        cls: type["ShopPortal"],
        connection: TraderaConnection,
        items: Sequence[SetQuantityShopItem],
        identity: bool = False,
    ) -> tuple[int, SetQuantityOnShopItemsResult | TraderaErrorResponse]:
        return await cls._send(
            connection,
            "PUT",
            f"{ENDPOINT}/quantities",
            SetQuantityOnShopItemsResult,
            auth="user",
            identity=identity,
            json={"shopItems": list(items)},
        )

    @classmethod
    async def set_activate_dates(
        cls: type["ShopPortal"],
        connection: TraderaConnection,
        items: Sequence[SetActivateDateShopItem],
        identity: bool = False,
    ) -> tuple[int, SetActivateDateOnShopItemsResult | TraderaErrorResponse]:
        return await cls._send(
            connection,
            "PUT",
            f"{ENDPOINT}/activate-dates",
            SetActivateDateOnShopItemsResult,
            auth="user",
            identity=identity,
            json={"shopItems": list(items)},
        )

    @classmethod
    async def settings(
        cls: type["ShopPortal"],
        connection: TraderaConnection,
        identity: bool = False,
    ) -> tuple[int, ShopSettingsData | TraderaErrorResponse]:
        return await cls._send(
            connection,
            "GET",
            SETTINGS,
            ShopSettingsData,
            auth="user",
            identity=identity,
        )

    @classmethod
    async def update_settings(
        cls: type["ShopPortal"],
        connection: TraderaConnection,
        settings: ShopSettingsData,
    ) -> tuple[int, None | TraderaErrorResponse]:
        return await cls._send(
            connection,
            "PUT",
            SETTINGS,
            type(None),
            auth="user",
            json=settings,
        )


__all__ = ("ShopPortal",)
