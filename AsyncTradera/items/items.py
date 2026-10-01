from ..common import (
    ActiveFilter,
    ActiveFilters,
    DateLike,
    Endpoints,
    Item,
    ItemTypeFilter,
    ItemTypeFilters,
    TraderaClient,
    TraderaConnection,
    TraderaErrorResponse,
)
from ._types import ItemAddedDescription, ItemQuickInfo, ItemRestarts

ENDPOINT = Endpoints.ITEMS.value


class ItemsPortal(TraderaClient):
    """
    Public item lookups. App auth only. For the authenticated seller's own view of an
    item, use ``ListingsPortal.get``.
    """

    @classmethod
    async def get(
        cls: type["ItemsPortal"],
        connection: TraderaConnection,
        item_id: int,
        identity: bool = False,
    ) -> tuple[int, Item | TraderaErrorResponse]:
        return await cls._send(
            connection, "GET", f"{ENDPOINT}/{item_id}", Item, identity=identity
        )

    @classmethod
    async def descriptions(
        cls: type["ItemsPortal"],
        connection: TraderaConnection,
        item_id: int,
        identity: bool = False,
    ) -> tuple[int, list[ItemAddedDescription] | TraderaErrorResponse]:
        """
        Descriptions the seller appended after the item was listed.
        """
        return await cls._send(
            connection,
            "GET",
            f"{ENDPOINT}/{item_id}/descriptions",
            list[ItemAddedDescription],
            identity=identity,
        )

    @classmethod
    async def restarts(
        cls: type["ItemsPortal"],
        connection: TraderaConnection,
        item_id: int,
        identity: bool = False,
    ) -> tuple[int, ItemRestarts | TraderaErrorResponse]:
        return await cls._send(
            connection,
            "GET",
            f"{ENDPOINT}/{item_id}/restarts",
            ItemRestarts,
            identity=identity,
        )

    @classmethod
    async def by_seller(
        cls: type["ItemsPortal"],
        connection: TraderaConnection,
        user_id: int,
        category_id: int | None = None,
        filter_active: ActiveFilter | ActiveFilters | None = None,
        min_end_date: DateLike | None = None,
        max_end_date: DateLike | None = None,
        filter_item_type: ItemTypeFilter | ItemTypeFilters | None = None,
        identity: bool = False,
    ) -> tuple[int, list[Item] | TraderaErrorResponse]:
        return await cls._send(
            connection,
            "GET",
            f"{ENDPOINT}/seller/{user_id}",
            list[Item],
            identity=identity,
            params={
                "categoryId": category_id,
                "filterActive": filter_active,
                "minEndDate": min_end_date,
                "maxEndDate": max_end_date,
                "filterItemType": filter_item_type,
            },
        )

    @classmethod
    async def seller_quick_info(
        cls: type["ItemsPortal"],
        connection: TraderaConnection,
        user_id: int,
        category_id: int | None = None,
        filter_active: ActiveFilter | ActiveFilters | None = None,
        filter_item_type: ItemTypeFilter | ItemTypeFilters | None = None,
        min_end_date: DateLike | None = None,
        max_end_date: DateLike | None = None,
        min_created_date: DateLike | None = None,
        max_created_date: DateLike | None = None,
        identity: bool = False,
    ) -> tuple[int, list[ItemQuickInfo] | TraderaErrorResponse]:
        """
        Ids, types and creation dates of a seller's items; cheaper than ``by_seller``.
        """
        return await cls._send(
            connection,
            "GET",
            f"{ENDPOINT}/seller/{user_id}/quick-info",
            list[ItemQuickInfo],
            identity=identity,
            params={
                "categoryId": category_id,
                "filterActive": filter_active,
                "filterItemType": filter_item_type,
                "minEndDate": min_end_date,
                "maxEndDate": max_end_date,
                "minCreatedDate": min_created_date,
                "maxCreatedDate": max_created_date,
            },
        )


__all__ = ("ItemsPortal",)
